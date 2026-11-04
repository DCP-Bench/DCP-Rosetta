"""Set up, check and pick this machine's container engine.

    make engine                                           # interactive
    python -m evaluation.engine_setup --check             # report only; exit 1 if the engine isn't ready
    python -m evaluation.engine_setup --engine apptainer --yes   # pick and fix without asking

It checks Docker, rootless podman and Apptainer, offers to fix what the chosen one
lacks, and saves the choice for this checkout (.dcp-engine.json; DCP_* environment
variables still override it). The fixes:

- Apptainer: installs an unprivileged Apptainer from the Apptainer PPA (Ubuntu), without
  root, into a folder you choose, and enables lingering so a systemd user manager runs.
- podman: writes ~/.config/containers/storage.conf (images on a local disk) and
  registries.conf (Docker-style short names), and enables lingering.

Then it lists which images are built and current, says how to get the others (on
Apptainer: build and export them on a machine with Docker, copy them over, convert
them here), and can run one evaluation as a smoke test.
"""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request

from . import engine as engines
from .execution import ROOT, integration, integration_folders, recipe
from .results import EvaluationError

PPA = "https://ppa.launchpadcontent.net/apptainer/ppa/ubuntu"
# Libraries every Ubuntu has, or tools unprivileged Apptainer without subuid ranges doesn't use.
SKIPPED_DEPENDS = {"libc6", "uidmap", "fakeroot"}
SMOKE = ("cpmpy_python", ROOT / "examples" / "abbots.py", "abbots_puzzle")


# ---- Small helpers ----------------------------------------------------------------------

def sh(*command, timeout=60, env=None):
    """(exit code, stdout+stderr) of a command, 127 if it isn't installed."""
    try:
        done = subprocess.run(command, capture_output=True, text=True, timeout=timeout, env=env)
    except FileNotFoundError:
        return 127, f"{command[0]}: not found"
    except subprocess.TimeoutExpired:
        return 124, f"{command[0]}: timed out"
    return done.returncode, (done.stdout + done.stderr).strip()


def filesystem(path):
    path = Path(path)
    while not path.exists() and path != path.parent:
        path = path.parent
    return sh("stat", "-f", "-c", "%T", str(path))[1]


def on_nfs(path):
    return filesystem(path).startswith("nfs")


class Prompt:
    def __init__(self, assume_yes, interactive):
        self.assume_yes, self.interactive = assume_yes, interactive

    def yes(self, question, default=True):
        if self.assume_yes:
            return True
        if not self.interactive:
            return False
        answer = input(f"{question} [{'Y/n' if default else 'y/N'}] ").strip().lower()
        return default if not answer else answer.startswith("y")

    def text(self, question, default):
        if self.assume_yes or not self.interactive:
            return default
        return input(f"{question} [{default}] ").strip() or default


class Check:
    """One engine's state: whether it is usable, and what is missing with its fix."""

    def __init__(self, name):
        self.name, self.version, self.notes, self.problems = name, None, [], []

    def problem(self, text, fix=None):
        self.problems.append((text, fix))

    @property
    def usable(self):
        return self.version is not None and not self.problems


def user_manager():
    """Whether a systemd user manager answers, after pointing at /run/user/$UID."""
    engines.Apptainer()  # sets XDG_RUNTIME_DIR and DBUS_SESSION_BUS_ADDRESS when they are missing
    return sh("systemctl", "--user", "show-environment", timeout=15)[0] == 0


def enable_linger(prompt):
    if not prompt.yes("No systemd user manager runs for you; enable lingering (`loginctl enable-linger`)?"):
        return False
    code, output = sh("loginctl", "enable-linger", os.environ.get("USER") or str(os.getuid()))
    if code:
        print(f"  loginctl failed: {output}\n  Ask an admin to run `loginctl enable-linger {os.environ.get('USER')}`.")
        return False
    for _ in range(50):
        if Path(f"/run/user/{os.getuid()}/bus").exists():
            break
        time.sleep(0.1)
    return user_manager()


def cpu_note(check):
    if "cpu" in engines.delegated_controllers():
        check.notes.append("CPU limit: quota (you own the cgroup cpu controller)")
    else:
        check.notes.append("CPU limit: whole cores per run (no cpu controller); set a core pool to share the machine")


# ---- Docker -----------------------------------------------------------------------------

def check_docker(prompt):
    check = Check("docker")
    code, output = sh("docker", "--version", timeout=15)
    if code == 127:
        check.problem("not installed")
        return check
    check.version = output
    code, output = sh("docker", "info", "--format", "{{.ServerVersion}}", timeout=30)
    if code:
        check.problem(f"the daemon does not answer: {output.splitlines()[-1] if output else code}")
    check.notes.append("CPU limit: quota")
    return check


# ---- podman -----------------------------------------------------------------------------

STORAGE_CONF = """\
# Written by `make engine` (DCP-Rosetta): images on a local disk; rootless without a
# subuid range needs fuse-overlayfs and ignore_chown_errors.
[storage]
driver = "overlay"
graphroot = "{graphroot}"

[storage.options.overlay]
mount_program = "{fuse}"
ignore_chown_errors = "true"
"""
REGISTRIES_CONF = """\
# Written by `make engine` (DCP-Rosetta): resolve bare image names as Docker does.
unqualified-search-registries = ["docker.io"]
short-name-mode = "permissive"
"""


def local_folder():
    """A folder on a local disk for big files: next to the checkout, unless that is on NFS."""
    return ROOT.parent if not on_nfs(ROOT) else Path(tempfile.gettempdir())


def check_podman(prompt, fix):
    check = Check("podman")
    code, output = sh("podman", "--version", timeout=15)
    if code == 127:
        check.problem("not installed (needs an admin: `apt install podman fuse-overlayfs`)")
        return check
    check.version = output
    config = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config") / "containers"
    _, graphroot = sh("podman", "info", "--format", "{{.Store.GraphRoot}}", timeout=60)
    if on_nfs(graphroot):
        check.problem(f"podman stores images on NFS ({graphroot})", lambda: write_storage_conf(config, prompt))
    if not shutil.which("fuse-overlayfs"):
        check.problem("fuse-overlayfs is missing (needs an admin)")
    if not shutil.which("gcc"):
        check.problem("gcc is missing; builds compile a small helper with it once")
    system = Path("/etc/containers/registries.conf")
    resolves = (config / "registries.conf").exists() or (system.exists() and "docker.io" in system.read_text(errors="ignore"))
    if not resolves:
        check.problem("bare image names (python:3.12) won't resolve", lambda: write_file(config / "registries.conf",
                                                                                         REGISTRIES_CONF, prompt))
    if not user_manager():
        check.problem("no systemd user manager (podman fails after you log out)", lambda: enable_linger(prompt))
    cpu_note(check)
    if fix:
        apply_fixes(check, prompt)
    return check


def write_file(path, text, prompt):
    if path.exists():
        print(f"  {path} exists:\n" + "".join(f"    {line}\n" for line in path.read_text().splitlines()))
        if not prompt.yes(f"  Replace it (the old one goes to {path.name}.bak)?", default=False):
            return False
        shutil.copy2(path, path.with_name(path.name + ".bak"))
    elif not prompt.yes(f"  Write {path}?"):
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    print(f"  wrote {path}")
    return True


def write_storage_conf(config, prompt):
    graphroot = Path(prompt.text("  Where should podman keep images (a local disk)?", str(local_folder() / "containers")))
    if on_nfs(graphroot):
        print(f"  {graphroot} is on NFS too; pick a local disk")
        return False
    if on_nfs(config):
        print(f"  Note: {config} is on NFS, so every machine sharing this home gets this graphroot.")
    return write_file(config / "storage.conf", STORAGE_CONF.format(graphroot=graphroot,
                                                                     fuse=shutil.which("fuse-overlayfs") or
                                                                     "/usr/bin/fuse-overlayfs"), prompt)


# ---- Apptainer --------------------------------------------------------------------------

def apptainer_binary(settings):
    for candidate in (engines.setting("DCP_APPTAINER"), settings.get("apptainer"), shutil.which("apptainer"),
                      str(local_folder() / "apptainer" / "bin" / "apptainer")):
        if candidate and Path(candidate).is_file() and os.access(candidate, os.X_OK):
            return candidate
    return None


def check_apptainer(prompt, fix, settings):
    check = Check("apptainer")
    binary = apptainer_binary(settings)
    if binary is None:
        check.problem("not installed", lambda: install_apptainer(prompt, settings))
    else:
        settings["apptainer"] = binary
        code, output = sh(binary, "--version", timeout=30)
        if code:
            check.problem(f"{binary} does not run: {output}")
        else:
            check.version = output
            major, minor = (int(part) for part in output.split()[-1].split(".")[:2])
            if (major, minor) < (1, 1):
                check.problem(f"{output} is too old; 1.1 or later runs unprivileged",
                              lambda: install_apptainer(prompt, settings))
    if int(Path("/proc/sys/user/max_user_namespaces").read_text() or 0) == 0:
        check.problem("unprivileged user namespaces are off (needs an admin: sysctl user.max_user_namespaces)")
    restrict = Path("/proc/sys/kernel/apparmor_restrict_unprivileged_userns")
    if restrict.exists() and restrict.read_text().strip() == "1":
        check.problem("AppArmor blocks unprivileged user namespaces (needs an admin: an AppArmor profile for apptainer)")
    if not user_manager():
        check.problem("no systemd user manager, which each run's limits need", lambda: enable_linger(prompt))
    cpu_note(check)
    if fix:
        apply_fixes(check, prompt)
        if check.version is None and apptainer_binary(settings):
            return check_apptainer(prompt, False, settings)
    return check


def install_apptainer(prompt, settings):
    """Unprivileged Apptainer from the PPA's .deb for this Ubuntu release, without root:
    unpacked with dpkg-deb, etc/ and var/ moved under usr/ so it finds them relative to
    its binary, missing libraries from `apt-get download`, and a wrapper bin/apptainer."""
    release = dict(line.split("=", 1) for line in Path("/etc/os-release").read_text().splitlines() if "=" in line)
    codename = release.get("VERSION_CODENAME", "").strip('"')
    if release.get("ID") != "ubuntu" or not codename or not shutil.which("dpkg-deb"):
        print("  The automatic install supports Ubuntu. Elsewhere, see\n"
              "  https://apptainer.org/docs/admin/main/installation.html#install-unprivileged-from-pre-built-binaries")
        return False
    prefix = Path(prompt.text("  Install Apptainer into (a local disk)?", str(local_folder() / "apptainer")))
    if not prompt.yes(f"  Install the Apptainer PPA's {codename} build into {prefix}?"):
        return False
    arch = sh("dpkg", "--print-architecture")[1]
    packages = fetch(f"{PPA}/dists/{codename}/main/binary-{arch}/Packages.gz")
    stanzas = [dict(line.split(": ", 1) for line in block.splitlines() if ": " in line)
               for block in gzip.decompress(packages).decode().split("\n\n")]
    package = next((s for s in stanzas if s.get("Package") == "apptainer"), None)
    if package is None:
        print(f"  The PPA has no apptainer for {codename}/{arch}")
        return False
    print(f"  downloading apptainer {package['Version']}")
    deb = fetch(f"{PPA}/{package['Filename']}")
    if hashlib.sha256(deb).hexdigest() != package["SHA256"]:
        print("  the download does not match the PPA's checksum")
        return False
    with tempfile.TemporaryDirectory() as temp:
        temp = Path(temp)
        (temp / "apptainer.deb").write_bytes(deb)
        if prefix.exists():
            shutil.rmtree(prefix)
        subprocess.run(["dpkg-deb", "-x", str(temp / "apptainer.deb"), str(prefix)], check=True)
        for folder in ("etc", "var"):
            if (prefix / folder).exists():
                shutil.move(str(prefix / folder), str(prefix / "usr" / folder))
        (prefix / "lib").mkdir()
        for dependency in package.get("Depends", "").split(","):
            name = dependency.split()[0] if dependency.strip() else ""
            if not name or name in SKIPPED_DEPENDS or sh("dpkg", "-s", name)[1].find("Status: install ok installed") >= 0:
                continue
            print(f"  adding {name}, which this machine lacks")
            code = subprocess.run(["apt-get", "download", name], cwd=temp, capture_output=True).returncode
            downloaded = sorted(temp.glob(f"{name}_*.deb"))
            if code or not downloaded:
                print(f"  could not download {name}; apptainer may lack it")
                continue
            unpacked = temp / name
            subprocess.run(["dpkg-deb", "-x", str(downloaded[-1]), str(unpacked)], check=True)
            for library in unpacked.rglob("*.so*"):
                shutil.copy2(library, prefix / "lib" / library.name, follow_symlinks=False)
    for folder in ("cache", "tmp", "bin"):
        (prefix / folder).mkdir(exist_ok=True)
    wrapper = prefix / "bin" / "apptainer"
    wrapper.write_text(f"""#!/bin/sh
# Unprivileged Apptainer {package['Version']} (the PPA's {codename} build, relocated), installed by `make engine`.
export LD_LIBRARY_PATH={prefix}/lib${{LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}}
export APPTAINER_CACHEDIR=${{APPTAINER_CACHEDIR:-{prefix}/cache}}
export APPTAINER_TMPDIR=${{APPTAINER_TMPDIR:-{prefix}/tmp}}
exec {prefix}/usr/bin/apptainer "$@"
""")
    wrapper.chmod(0o755)
    code, output = sh(str(wrapper), "--version")
    print(f"  {wrapper}: {output}")
    if code == 0:
        settings["apptainer"] = str(wrapper)
    return code == 0


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": "dcp-rosetta-engine-setup"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


# ---- Common -----------------------------------------------------------------------------

def apply_fixes(check, prompt):
    remaining = []
    for text, fix in check.problems:
        if fix is None:
            remaining.append((text, fix))
            continue
        print(f"{check.name}: {text}")
        if not fix():
            remaining.append((text, fix))
    check.problems = remaining


def report(checks, chosen):
    for check in checks.values():
        mark = "ready" if check.usable else "missing" if check.version is None else "needs work"
        print(f"{'*' if check.name == chosen else ' '} {check.name:<10} {mark:<14} {check.version or ''}")
        for text, fix in check.problems:
            print(f"      - {text}{' (fixable)' if fix else ''}")
        if check.version:
            for note in check.notes:
                print(f"      {note}")


def image_states(engine):
    """{id: "current" | "stale" | "missing"} for every integration."""
    states = {}
    for solver_id in integration_folders():
        try:
            built = engine.image_recipe(integration(solver_id))
        except EvaluationError:
            states[solver_id] = "missing"
            continue
        states[solver_id] = "current" if built == recipe(solver_id) else "stale"
    return states


def next_steps(engine, states):
    todo = sorted(i for i, state in states.items() if state != "current")
    print(f"\nImages: {len(states) - len(todo)} current, {sum(s == 'stale' for s in states.values())} stale, "
          f"{sum(s == 'missing' for s in states.values())} missing (of {len(states)}).")
    if not todo:
        return
    # With no IDs, build and export do every integration.
    ids = " " + " ".join(todo) if len(todo) <= 8 else ""
    scope = f"the {len(todo)} that aren't current" if ids else f"all of them ({len(todo)} aren't current; name IDs to do fewer)"
    if engine.name != "apptainer":
        print(f"Build {scope}:\n  python -m evaluation.build{ids}")
        return
    code, commit = sh("git", "-C", str(ROOT), "rev-parse", "--short", "HEAD")
    commit = f" ({commit})" if code == 0 else ""
    print(f"""Apptainer can't build from Dockerfiles. Get {scope} from a machine with
Docker or podman, in a checkout of the same commit{commit}:

  python -m evaluation.build{ids}
  python -m evaluation.export --to exported/{ids}
  rsync -a --progress exported/ {os.environ.get("USER", "")}@{socket.getfqdn()}:{ROOT}/exported/

and then here:

  python -m evaluation.build --archive exported/{ids}
  rm -r exported/            # the .tar files are no longer needed""")


def smoke(engine, prompt):
    solver_id, model, problem = SMOKE
    from . import evaluate
    if not prompt.yes(f"Run one evaluation as a smoke test ({solver_id}, {problem})?"):
        return True
    result = evaluate(model, problem, solver_id)
    print(f"  accepted={result['accepted']} reason={result['reason']} engine={result.get('engine')}")
    return result["accepted"]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="report only, change nothing")
    parser.add_argument("--engine", choices=engines.ENGINES, help="pick this engine without asking")
    parser.add_argument("--yes", action="store_true", help="apply every fix without asking")
    parser.add_argument("--taskset", help="the cores evaluations may use, e.g. 0-31 (with whole-core CPU limits)")
    args = parser.parse_args()
    interactive = sys.stdin.isatty() and not args.check and not args.yes
    prompt = Prompt(args.yes, interactive)
    settings = engines.saved()
    print(f"Container engines on {platform.node()} (checkout {ROOT}):\n")
    checks = {"docker": check_docker(prompt), "podman": check_podman(prompt, False),
              "apptainer": check_apptainer(prompt, False, settings)}
    chosen = args.engine or settings.get("engine") or next((n for n, c in checks.items() if c.usable), None) \
        or next((n for n, c in checks.items() if c.version or any(f for _, f in c.problems)), "docker")
    report(checks, chosen)
    if args.check:
        sys.exit(0 if checks[chosen].usable else 1)
    if interactive and not args.engine:
        answer = prompt.text(f"\nWhich engine should this checkout use ({'/'.join(engines.ENGINES)})?", chosen)
        if answer not in engines.ENGINES:
            sys.exit(f"Unknown engine {answer!r}")
        chosen = answer
    print()
    check = {"docker": lambda: check_docker(prompt), "podman": lambda: check_podman(prompt, True),
             "apptainer": lambda: check_apptainer(prompt, True, settings)}[chosen]()
    if not check.usable:
        report({chosen: check}, chosen)
        sys.exit(f"\n{chosen} is not ready; fix the items above and run `make engine` again.")
    settings["engine"] = chosen
    if chosen == "apptainer":
        settings.setdefault("apptainer_images", str(ROOT / "images"))
    if args.taskset:
        settings["taskset"] = args.taskset
    elif "cpu" not in engines.delegated_controllers() and chosen != "docker":
        pool = prompt.text("Cores evaluations may use (whole cores per run; `all` for every core)",
                           settings.get("taskset") or "all")
        if pool == "all":
            settings.pop("taskset", None)
        else:
            settings["taskset"] = pool
    engines.CONFIG.write_text(json.dumps(settings, indent=2) + "\n")
    print(f"{chosen} is ready: {check.version}. Saved to {engines.CONFIG.name}.")
    for variable in engines.SETTINGS:
        if os.environ.get(variable):
            print(f"  note: {variable}={os.environ[variable]} in your environment overrides the saved setting")
    engines.current.cache_clear()
    engine = engines.current()
    states = image_states(engine)
    next_steps(engine, states)
    if states.get(SMOKE[0]) == "current":
        print()
        if not smoke(engine, prompt):
            sys.exit("The smoke test was not accepted; see the result above.")


if __name__ == "__main__":
    main()
