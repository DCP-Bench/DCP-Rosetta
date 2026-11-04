"""The container engines that build and run the integration images.

`DCP_ENGINE` picks one; unset, the first of docker, podman and apptainer found on
PATH is used.

- `docker`: the reference. Every limit is Docker's own.
- `podman`: rootless podman, also for a user without an /etc/subuid range or `cpu`
  cgroup delegation. It builds from the same Dockerfiles.
- `apptainer`: unprivileged Apptainer, for machines with neither. It cannot build from
  a Dockerfile: images are built with Docker or podman elsewhere, exported with
  `python -m evaluation.export` and converted here with `python -m evaluation.build
  --archive DIR`. Each run is a transient systemd user service, which bounds its memory,
  tasks and CPUs and reports the kernel's OOM kill.

A run's CPU limit is a quota where the engine can set one (Docker; podman and Apptainer
when the user owns the cgroup `cpu` controller). Otherwise the run gets ceil(cpus)
cores of its own (`CoreClaim`) and may not widen its affinity. `describe` reports which,
and every result records it.
"""
import fcntl
import functools
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time
import uuid

from .execution import PLATFORM, RECIPE_LABEL, ROOT, integration_folder, run_process
from .results import EvaluationError

ENGINES = ("docker", "podman", "apptainer")
NAME_PREFIX = "dcp-eval-"
PIDS_LIMIT = 128
TMP_BYTES = 536870912
PODMAN_ASSETS = ROOT / "tools" / "podman"
CACHE = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache") / "dcp-rosetta"


@functools.cache
def current():
    """The engine this process uses: `DCP_ENGINE`, else the first one installed."""
    name = os.environ.get("DCP_ENGINE")
    if not name:
        name = next((n for n in ENGINES if shutil.which(os.environ.get("DCP_APPTAINER", n) if n == "apptainer" else n)),
                    "docker")
    if name not in ENGINES:
        raise EvaluationError("infrastructure_error", f"DCP_ENGINE={name!r}; use one of {', '.join(ENGINES)}")
    return {"docker": Docker, "podman": Podman, "apptainer": Apptainer}[name]()


class Run:
    """One finished container run."""

    def __init__(self, code, stdout, stderr, oom_killed, readings=None):
        self.code, self.stdout, self.stderr = code, stdout, stderr
        self.oom_killed, self.readings = oom_killed, readings


# ---- CPU limits without a cpu controller -------------------------------------------------

def delegated_controllers():
    """The cgroup controllers this user's containers can use: the systemd user manager's
    (where systemd places podman's and Apptainer's units), else this process's cgroup's."""
    uid = os.getuid()
    path = Path(f"/sys/fs/cgroup/user.slice/user-{uid}.slice/user@{uid}.service/cgroup.controllers")
    if not path.is_file():
        try:
            path = Path("/sys/fs/cgroup" + Path("/proc/self/cgroup").read_text().splitlines()[0].split(":", 2)[2]) \
                / "cgroup.controllers"
        except (OSError, IndexError):
            return set()
    try:
        return set(path.read_text().split())
    except OSError:
        return set()


def parse_cpu_list(text):
    """"0-3,8" -> [0, 1, 2, 3, 8]"""
    cores = []
    for part in filter(None, text.replace(" ", "").split(",")):
        low, _, high = part.partition("-")
        cores += range(int(low), int(high or low) + 1)
    return cores


class CoreClaim:
    """ceil(cpus) cores of the pool held for one run, by an flock per core, so concurrent
    runs on this machine never share a core. The pool is `DCP_TASKSET` (e.g. "0-7"), else
    every core this process may use. Released on `release` or when the process ends."""

    def __init__(self, cpus):
        count = max(1, math.ceil(cpus))
        pool = parse_cpu_list(os.environ["DCP_TASKSET"]) if os.environ.get("DCP_TASKSET") \
            else sorted(os.sched_getaffinity(0))
        folder = Path(os.environ.get("XDG_RUNTIME_DIR") or tempfile.gettempdir()) / f"dcp-cores-{os.getuid()}"
        folder.mkdir(parents=True, exist_ok=True)
        self.cores, self._files = [], []
        for core in pool:
            handle = open(folder / f"{core}.lock", "w")
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError:
                handle.close()
                continue
            self.cores.append(core)
            self._files.append(handle)
            if len(self.cores) == count:
                return
        self.release()
        raise EvaluationError("infrastructure_error", f"No {count} free core(s) in the pool "
                                                      f"{','.join(map(str, pool))}: run fewer evaluations at once "
                                                      "or widen DCP_TASKSET")

    @property
    def text(self):
        return ",".join(map(str, self.cores))

    def release(self):
        for handle in self._files:
            handle.close()
        self._files = []


# ---- Docker -----------------------------------------------------------------------------

class Docker:
    name = command = "docker"
    OOM_REREADS = 8
    OOM_REREAD_INTERVAL = 0.25

    def version(self):
        code, stdout, stderr = run_process([self.command, "--version"], 15)
        if code:
            raise EvaluationError("infrastructure_error", f"Could not run {self.command}: {stderr.strip()}")
        return stdout.strip()

    def cpu_limit(self):
        return "quota"

    @functools.cache
    def describe(self):
        """What runs the containers, recorded with every result."""
        return {"name": self.name, "version": self.version(), "cpu_limit": self.cpu_limit()}

    def _inspect(self, metadata, template):
        code, stdout, stderr = run_process([self.command, "image", "inspect", metadata["image"], "--format", template], 15)
        if code:
            raise EvaluationError("infrastructure_error", f"Image unavailable; start {self.name} and explicitly build "
                                                          f"{metadata['id']}. {stderr.strip()}")
        return stdout.strip()

    def image_identity(self, metadata):
        """The local image ID. It names the bytes run on this machine only; see execution.recipe."""
        identity = self._inspect(metadata, "{{.Id}}")
        if re.fullmatch(r"[0-9a-f]{64}", identity):
            identity = "sha256:" + identity  # podman prints the bare digest
        if not identity.startswith("sha256:"):
            raise EvaluationError("infrastructure_error", f"{self.name} did not return an image identity")
        return identity

    def image_recipe(self, metadata):
        """The recipe digest evaluation.build stamped on the local image, or None if it has none."""
        try:
            labels = json.loads(self._inspect(metadata, "{{json .Config.Labels}}")) or {}
        except ValueError as error:
            raise EvaluationError("infrastructure_error", f"{self.name} returned unreadable labels: {error}") from error
        return labels.get(RECIPE_LABEL)

    # Building

    def build_command(self, metadata, recipe, dockerfile, extra=()):
        return [self.command, "build", f"--platform={PLATFORM}", "-t", metadata["image"],
                "--label", f"{RECIPE_LABEL}={recipe}", *extra, "-f", str(dockerfile), str(ROOT)]

    def build(self, solver_id, metadata, recipe, extra=(), archive=None):
        if archive:
            raise SystemExit(f"{self.name} builds from Dockerfiles; --archive is for apptainer")
        subprocess.run(self.build_command(metadata, recipe, integration_folder(solver_id) / "Dockerfile", extra),
                       check=True)

    def save(self, metadata, path):
        """Write the image as a docker-archive tar, which Apptainer converts."""
        subprocess.run([self.command, "save", "-o", str(path), metadata["image"]], check=True)

    # Running

    def user(self):
        return "--user=65534:65534"

    def run_command(self, name, image, staging, memory_mb, cpus, entrypoint, args):
        return [self.command, "run", "--pull=never", "--name", name,
                "--network=none", "--read-only", self.user(), "--cap-drop=ALL",
                "--security-opt=no-new-privileges", f"--pids-limit={PIDS_LIMIT}", "--log-driver=none",
                "--memory", f"{memory_mb}m", "--memory-swap", f"{memory_mb}m", *self.cpu_options(cpus),
                "--tmpfs", f"/tmp:rw,exec,nosuid,size={TMP_BYTES},mode=1777",
                "--mount", f"type=bind,source={staging},target=/input,readonly",
                "--workdir=/tmp", "--env=HOME=/tmp", "--env=PYTHONDONTWRITEBYTECODE=1",
                *(["--entrypoint", entrypoint] if entrypoint else []), image, *args]

    def cpu_options(self, cpus):
        return ["--cpus", str(cpus)]

    def run(self, metadata, image, staging, *, memory_mb, cpus, timeout, entrypoint=None, args=()):
        """Run `image` (the identity image_identity returned, so exactly the bytes a result
        names) on the files in `staging`, mounted read-only at /input, under the evaluator's
        isolation and limits. `entrypoint`/`args` replace the image's own."""
        name = NAME_PREFIX + uuid.uuid4().hex
        # No --rm: the container has to outlive its exit so killed_for_memory can inspect it.
        command = self.run_command(name, image, staging, memory_mb, cpus, entrypoint, list(args))
        try:
            return self._run(command, name, timeout)
        finally:
            self.remove(name)

    def _run(self, command, name, timeout):
        code, stdout, stderr = run_process(command, timeout)
        try:
            oom_killed, readings = self.killed_for_memory(name, code)
        except EvaluationError as error:
            raise EvaluationError(error.reason, f"{error.detail}; the run exited {code}: {stderr[-4000:]}") from error
        return Run(code, stdout, stderr, oom_killed, readings)

    def oom_flag(self, name):
        code, stdout, stderr = run_process([self.command, "inspect", "--format", "{{.State.OOMKilled}}", name], 15)
        if code or stdout.strip() not in ("true", "false"):
            raise EvaluationError("infrastructure_error", f"Could not inspect container {name}: {stderr.strip()}")
        return stdout.strip() == "true"

    def killed_for_memory(self, name, exit_code):
        """Whether the kernel killed any process in the exited container at its memory limit.

        Docker sets this for the runner and for a solver process the runner started
        alike, and exit 137 alone cannot tell it apart from a SIGKILL a submission
        sent itself. Docker can record the kill after the exit that `docker run`
        returns on, so after an exit 137 an unset flag is read again for up to
        OOM_REREADS * OOM_REREAD_INTERVAL seconds. Returns the flag and, after an
        exit 137, the readings for the detail of the failed run.
        """
        first = self.oom_flag(name)
        if exit_code != 137:
            return first, None
        if first:
            return True, "OOMKilled was true at exit"
        later = False
        for reread in range(1, self.OOM_REREADS + 1):
            time.sleep(self.OOM_REREAD_INTERVAL)
            later = self.oom_flag(name)
            if later:
                break
        return later, f"OOMKilled was false at exit and {str(later).lower()} {reread * self.OOM_REREAD_INTERVAL:g} s later"

    def remove(self, name):
        """Remove the container; killing the client alone does not stop it."""
        try:
            code, _, detail = run_process([self.command, "rm", "--force", name], 15)
            if code and "no such container" not in detail.lower():  # Docker capitalises, podman not
                raise EvaluationError("infrastructure_error", f"Container cleanup failed for {name}: {detail}")
        except EvaluationError as error:
            raise EvaluationError("infrastructure_error", f"Could not confirm cleanup of {name}: {error}") from error

    def leftovers(self):
        """Evaluator containers still present, which a finished evaluation never leaves."""
        _, stdout, _ = run_process([self.command, "ps", "-a", "--filter", f"name={NAME_PREFIX}",
                                    "--format", "{{.Names}}"], 15)
        return stdout.split()

    def tool(self, metadata, entrypoint, args, *, network=False, root=False, timeout=None):
        """A trusted helper run in the image (lock, regressions): no submission, no limits."""
        command = [self.command, "run", "--rm", "--pull=never", *([] if network else ["--network=none"]),
                   *(["--user=0"] if root else []), "--entrypoint", entrypoint, metadata["image"], *args]
        return subprocess.run(command, capture_output=True, text=True, timeout=timeout)


# ---- Rootless podman --------------------------------------------------------------------

class Podman(Docker):
    """Rootless podman, including for a user without a subuid range or cpu delegation.

    Without a subuid range the container has a single uid, so runs use its root, which
    is the unprivileged invoking user; every other restriction stays. Builds get an apt
    setting so apt does not switch to `_apt`, a preloaded no-op chown so tar and dpkg do
    not fail on owners the namespace lacks, and a Dockerfile copy without `ADD
    --checksum`, which podman 3.x rejects (the checksum is checked by sha256sum instead).
    """
    name = command = "podman"

    def cpu_limit(self):
        return "quota" if "cpu" in delegated_controllers() else "cores"

    def user(self):
        return "--user=0:0"

    def cpu_options(self, cpus):
        return ["--cpus", str(cpus)] if self.cpu_limit() == "quota" else []

    def run(self, metadata, image, staging, *, memory_mb, cpus, timeout, entrypoint=None, args=()):
        if self.cpu_limit() == "quota":
            return super().run(metadata, image, staging, memory_mb=memory_mb, cpus=cpus, timeout=timeout,
                               entrypoint=entrypoint, args=args)
        claim = CoreClaim(cpus)
        try:
            name = NAME_PREFIX + uuid.uuid4().hex
            command = self.run_command(name, image, staging, memory_mb, cpus, entrypoint, list(args))
            # The seccomp profile keeps the candidate on its cores: podman's default
            # without sched_setaffinity, which then fails with EPERM.
            command[2:2] = [f"--security-opt=seccomp={self.seccomp_profile()}"]
            try:
                return self._run(["taskset", "-c", claim.text, *command], name, timeout)
            finally:
                self.remove(name)
        finally:
            claim.release()

    @staticmethod
    def seccomp_profile():
        source = Path(os.environ.get("DCP_SECCOMP_DEFAULT", "/usr/share/containers/seccomp.json"))
        target = CACHE / "seccomp-no-setaffinity.json"
        if target.is_file() and source.is_file() and target.stat().st_mtime >= source.stat().st_mtime:
            return target
        try:
            profile = json.loads(source.read_text())
        except (OSError, ValueError) as error:
            raise EvaluationError("infrastructure_error", f"No seccomp profile at {source} to derive the core-pinning "
                                                          f"one from (set DCP_SECCOMP_DEFAULT): {error}") from error
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(without_setaffinity(profile)))
        return target

    def build(self, solver_id, metadata, recipe, extra=(), archive=None):
        if archive:
            raise SystemExit("podman builds from Dockerfiles; --archive is for apptainer")
        CACHE.mkdir(parents=True, exist_ok=True)
        nochown, preload = CACHE / "nochown.so", CACHE / "ld.so.preload"
        if not nochown.is_file():
            subprocess.run(["gcc", "-O2", "-shared", "-fPIC", "-nostdlib", "-o", str(nochown),
                            str(PODMAN_ASSETS / "nochown.c")], check=True)
        preload.write_text("/usr/local/lib/dcp-nochown.so\n")
        graphroot = subprocess.run(["podman", "info", "--format", "{{.Store.GraphRoot}}"],
                                   capture_output=True, text=True).stdout.strip()
        filesystem = subprocess.run(["stat", "-f", "-c", "%T", graphroot], capture_output=True, text=True).stdout.strip()
        if filesystem == "nfs":
            print(f"warning: podman stores images on NFS ({graphroot}); set graphroot to a local disk, "
                  "see evaluation/README.md")
        mounts = ["-v", f"{PODMAN_ASSETS / 'apt-no-sandbox.conf'}:/etc/apt/apt.conf.d/00-no-sandbox:ro",
                  "-v", f"{nochown}:/usr/local/lib/dcp-nochown.so:ro",
                  "-v", f"{preload}:/etc/ld.so.preload:ro"]
        dockerfile = integration_folder(solver_id) / "Dockerfile"
        text = dockerfile.read_text(encoding="utf-8")
        rewritten = rewrite_add_checksum(text)
        with tempfile.NamedTemporaryFile("w", suffix=".Dockerfile", delete=False) as copy:
            copy.write(rewritten)
        try:
            command = self.build_command(metadata, recipe, copy.name if rewritten != text else dockerfile, extra)
            command[2:2] = mounts
            subprocess.run(command, check=True)
        finally:
            os.unlink(copy.name)

    def save(self, metadata, path):
        subprocess.run(["podman", "save", "--format", "docker-archive", "-o", str(path), metadata["image"]], check=True)

    def tool(self, metadata, entrypoint, args, *, network=False, root=False, timeout=None):
        command = ["podman", "run", "--rm", "--pull=never", *([] if network else ["--network=none"]),
                   "--user=0:0", "--entrypoint", entrypoint, metadata["image"], *args]
        return subprocess.run(command, capture_output=True, text=True, timeout=timeout)


def without_setaffinity(profile):
    """A seccomp profile like `profile` in which sched_setaffinity fails with EPERM."""
    profile = json.loads(json.dumps(profile))
    for rule in profile["syscalls"]:
        if "sched_setaffinity" in rule.get("names", []):
            rule["names"].remove("sched_setaffinity")
    profile["syscalls"] = [rule for rule in profile["syscalls"] if rule.get("names")]
    profile["syscalls"].append({"names": ["sched_setaffinity"], "action": "SCMP_ACT_ERRNO", "errnoRet": 1})
    return profile


ADD_CHECKSUM = re.compile(r"^ADD[ \t]+--checksum=sha256:([0-9a-f]{64})[ \t]*((?:[^\n]*\\\n)*[^\n]*)\n", re.MULTILINE)


def rewrite_add_checksum(text):
    """`ADD --checksum=sha256:H SRC DEST` -> `ADD SRC DEST` and `RUN ... sha256sum -c`,
    for builders without ADD --checksum (podman 3.x); the checksum is still enforced."""
    def fix(match):
        sha, rest = match.group(1), match.group(2).replace("\\\n", " ").split()
        return f"ADD {' '.join(rest)}\nRUN echo '{sha}  {rest[-1]}' | sha256sum -c -\n"
    return ADD_CHECKSUM.sub(fix, text)


# ---- Apptainer --------------------------------------------------------------------------

class Apptainer:
    """Unprivileged Apptainer on SIF images, each run a transient systemd user service.

    Images: `DCP_APPTAINER_IMAGES` (default images/ in the repository) holds
    <integration>.sif, converted from a docker-archive by `evaluation.build --archive`.
    The SIF keeps the image's labels, so its recipe reads as Docker's does; its identity
    is the SHA-256 of the SIF file, which names the bytes run here.

    A run is `systemd-run --user` around `apptainer run`, because unprivileged
    Apptainer can set no cgroup limit or seccomp filter itself: the unit carries the
    memory limit (MemoryMax, no swap), the task limit, and the CPU limit (CPUQuota with
    a delegated cpu controller, else claimed cores with CPUAffinity and a filter that
    makes sched_setaffinity fail with EPERM). systemd records the kernel's OOM kill as
    the unit's result. The container itself has no network, a read-only image and
    /input, a per-run scratch directory as /tmp (bounded by the disk, not 512 MB as
    under Docker), no capabilities, and the invoking user's uid.
    """
    name = "apptainer"
    # Apptainer's own processes (starter, squashfuse) take about 23 tasks of the unit.
    TASKS_OVERHEAD = 32

    def __init__(self):
        self.command = os.environ.get("DCP_APPTAINER", "apptainer")
        self.images = Path(os.environ.get("DCP_APPTAINER_IMAGES") or ROOT / "images")
        # ssh sessions on some servers get no systemd session; the user manager is still
        # reachable on its runtime directory when lingering is enabled.
        runtime = f"/run/user/{os.getuid()}"
        if not os.environ.get("XDG_RUNTIME_DIR") and os.path.isdir(runtime):
            os.environ["XDG_RUNTIME_DIR"] = runtime
        if not os.environ.get("DBUS_SESSION_BUS_ADDRESS") and os.path.exists(f"{runtime}/bus"):
            os.environ["DBUS_SESSION_BUS_ADDRESS"] = f"unix:path={runtime}/bus"

    def version(self):
        code, stdout, stderr = run_process([self.command, "--version"], 15)
        if code:
            raise EvaluationError("infrastructure_error", f"Could not run {self.command}: {stderr.strip()}")
        return stdout.strip()

    def cpu_limit(self):
        return "quota" if "cpu" in delegated_controllers() else "cores"

    @functools.cache
    def describe(self):
        code, _, stderr = run_process(["systemctl", "--user", "show-environment"], 15)
        if code:
            raise EvaluationError("infrastructure_error", "Apptainer runs need a systemd user manager for their limits, "
                                                          f"and `systemctl --user` cannot reach one ({stderr.strip()}); "
                                                          "enable lingering with `loginctl enable-linger`")
        return {"name": self.name, "version": self.version(), "cpu_limit": self.cpu_limit()}

    def sif(self, metadata):
        path = self.images / f"{metadata['id']}.sif"
        if not path.is_file():
            raise EvaluationError("infrastructure_error", f"Image unavailable: no {path}; export {metadata['id']} where "
                                                          "it is built and convert it with `evaluation.build --archive`")
        return path

    def image_identity(self, metadata):
        path = self.sif(metadata)
        stat = path.stat()
        return _file_digest(str(path), stat.st_size, stat.st_mtime_ns)

    def image_recipe(self, metadata):
        code, stdout, stderr = run_process([self.command, "inspect", "--labels", str(self.sif(metadata))], 60)
        if code:
            raise EvaluationError("infrastructure_error", f"Could not read the labels of {metadata['id']}: {stderr.strip()}")
        for line in stdout.splitlines():
            key, _, value = line.partition(":")
            if key.strip() == RECIPE_LABEL:
                return value.strip()
        return None

    def build(self, solver_id, metadata, recipe, extra=(), archive=None):
        """Convert <archive>/<id>.tar (from `evaluation.export`) into the SIF image."""
        if not archive:
            raise SystemExit("apptainer cannot build from a Dockerfile: build the image with docker or podman, "
                             "export it with `python -m evaluation.export`, and pass that folder as --archive")
        tar = Path(archive) / f"{solver_id}.tar"
        if not tar.is_file():
            raise SystemExit(f"{solver_id}: no {tar}")
        self.images.mkdir(parents=True, exist_ok=True)
        target = self.images / f"{solver_id}.sif"
        subprocess.run([self.command, "build", "--force", str(target), f"docker-archive:{tar}"], check=True)
        built = self.image_recipe(metadata)
        if built != recipe:
            print(f"warning: {solver_id}: the archive's recipe {built} is not this checkout's {recipe}")

    def save(self, metadata, path):
        raise SystemExit("export images where they are built, with docker or podman")

    def unit_properties(self, memory_mb, cpus, claim):
        properties = [f"MemoryMax={memory_mb}M", "MemorySwapMax=0", f"TasksMax={PIDS_LIMIT + self.TASKS_OVERHEAD}"]
        if claim is None:
            properties.append(f"CPUQuota={round(cpus * 100)}%")
        else:
            properties += [f"CPUAffinity={claim.text}", "SystemCallFilter=~sched_setaffinity",
                           "SystemCallErrorNumber=EPERM"]
        return [option for value in properties for option in ("-p", value)]

    def run_command(self, unit, sif, staging, scratch, properties, entrypoint, args, network=False):
        return ["systemd-run", "--user", "--quiet", "--pipe", "--wait", "--unit", unit, *properties,
                self.command, "exec" if entrypoint else "run", "--containall", "--cleanenv", "--no-home",
                *([] if network else ["--net", "--network", "none"]),
                "--workdir", str(scratch), "--bind", f"{staging}:/input:ro", "--pwd", "/tmp", "--home", "/tmp",
                "--env", "PYTHONDONTWRITEBYTECODE=1", str(sif), *([entrypoint] if entrypoint else []), *args]

    def run(self, metadata, image, staging, *, memory_mb, cpus, timeout, entrypoint=None, args=()):
        sif = self.sif(metadata)
        claim = None if self.cpu_limit() == "quota" else CoreClaim(cpus)
        unit = NAME_PREFIX + uuid.uuid4().hex
        scratch = Path(tempfile.mkdtemp(prefix="dcp_scratch_"))
        try:
            command = self.run_command(unit, sif, staging, scratch, self.unit_properties(memory_mb, cpus, claim),
                                       entrypoint, list(args))
            code, stdout, stderr = run_process(command, timeout)
            result, loaded = self.unit_state(unit)
            if code and not loaded and result == "success":
                # The unit never ran or left no state: systemd-run itself failed.
                raise EvaluationError("infrastructure_error", f"systemd-run exited {code}: {stderr[-4000:]}")
            oom_killed = result == "oom-kill"
            return Run(code, stdout, stderr, oom_killed, f"unit result {result}" if code else None)
        finally:
            self.remove(unit)
            shutil.rmtree(scratch, ignore_errors=True)
            if claim:
                claim.release()

    def unit_state(self, unit):
        """(Result, loaded) of the unit: a unit that succeeded is unloaded at once."""
        code, stdout, stderr = run_process(["systemctl", "--user", "show", "-p", "Result", "-p", "LoadState", unit], 15)
        if code:
            raise EvaluationError("infrastructure_error", f"Could not inspect unit {unit}: {stderr.strip()}")
        state = dict(line.split("=", 1) for line in stdout.splitlines() if "=" in line)
        return state.get("Result", ""), state.get("LoadState") == "loaded"

    def remove(self, unit):
        """Stop the unit, which kills a container the timeout left running, and forget it."""
        run_process(["systemctl", "--user", "stop", unit], 30)
        run_process(["systemctl", "--user", "reset-failed", unit], 15)
        _, state = self.unit_state(unit)
        if state:
            raise EvaluationError("infrastructure_error", f"Could not confirm cleanup of unit {unit}")

    def leftovers(self):
        _, stdout, _ = run_process(["systemctl", "--user", "list-units", "--all", "--plain", "--no-legend",
                                    f"{NAME_PREFIX}*"], 15)
        return [line.split()[0] for line in stdout.splitlines() if line.strip()]

    def tool(self, metadata, entrypoint, args, *, network=False, root=False, timeout=None):
        # root: Apptainer runs as the invoking user, which is enough to read an image.
        command = [self.command, "exec", "--containall", "--cleanenv", *([] if network else ["--net", "--network", "none"]),
                   str(self.sif(metadata)), entrypoint, *args]
        return subprocess.run(command, capture_output=True, text=True, timeout=timeout)


@functools.cache
def _file_digest(path, size, mtime_ns):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while chunk := handle.read(1 << 20):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()
