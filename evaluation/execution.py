"""Resource-bounded container execution (see evaluation.engine). No implicit builds or dependency installation."""
import hashlib
import json
from pathlib import Path
import shlex
import subprocess
import tempfile
import threading
import time

from .results import EvaluationError, strict_json

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_LIMIT = 8 * 1024 * 1024
PLATFORM = "linux/amd64"
# The image label evaluation.build stamps with the integration's recipe digest.
RECIPE_LABEL = "org.dcp-rosetta.recipe"


def run_process(command, timeout, input_bytes=None):
    """Drain both pipes with bounded memory, including malicious/noisy programs."""
    try:
        process = subprocess.Popen(command, stdin=subprocess.PIPE if input_bytes is not None else subprocess.DEVNULL,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError as e:
        raise EvaluationError("infrastructure_error", str(e)) from e
    buffers = [bytearray(), bytearray()]
    overflow = threading.Event()

    def drain(pipe, buffer):
        while chunk := pipe.read(65536):
            remaining = OUTPUT_LIMIT - len(buffer)
            buffer.extend(chunk[:max(0, remaining)])
            if len(chunk) > remaining:
                overflow.set()
                process.kill()
        pipe.close()

    threads = [threading.Thread(target=drain, args=(pipe, buffer), daemon=True)
               for pipe, buffer in zip((process.stdout, process.stderr), buffers)]
    for thread in threads:
        thread.start()
    if input_bytes is not None:
        try:
            process.stdin.write(input_bytes)
            process.stdin.close()
        except BrokenPipeError:
            pass
    try:
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired as e:
        process.kill()
        process.wait()
        raise EvaluationError("execution_timeout", f"Process exceeded {timeout} seconds") from e
    finally:
        for thread in threads:
            thread.join(5)
    if overflow.is_set():
        raise EvaluationError("output_limit", "Runner output exceeded 8 MiB")
    return process.returncode, *(b.decode("utf-8", errors="replace") for b in buffers)


def integration_folders(root=ROOT):
    """Every integration's folder by ID, in ID order.

    An integration is a folder holding metadata.json: `solvers/<id>/`, or, beside
    the skill its solver's bindings share, `solvers/<solver>/<interface>/`. A nested
    integration's ID is the `id` in its metadata.json, so an integration keeps its ID
    (and with it its image and models) when it moves; `<solver>_<interface>` is the
    convention for new ones and the fallback when metadata.json has no readable ID.
    A folder under a flat integration is part of it, not an integration of its own.
    """
    solvers = Path(root) / "solvers"
    folders = {path.parent.name: path.parent for path in solvers.glob("*/metadata.json")}
    for path in solvers.glob("*/*/metadata.json"):
        solver = path.parent.parent
        if (solver / "metadata.json").is_file():
            continue
        try:
            solver_id = strict_json(path.read_text(encoding="utf-8"))["id"]
        except (OSError, ValueError, KeyError, TypeError, EvaluationError):
            solver_id = None
        if not isinstance(solver_id, str) or not solver_id:
            solver_id = f"{solver.name}_{path.parent.name}"
        if solver_id in folders:
            raise EvaluationError("infrastructure_error",
                                  f"Two folders claim integration {solver_id}: {folders[solver_id]} and {path.parent}")
        folders[solver_id] = path.parent
    return dict(sorted(folders.items()))


def integration_folder(solver_id, root=ROOT):
    """The folder of one integration (see integration_folders); it need not exist yet,
    so a missing integration reads as `solvers/<id>/`."""
    return integration_folders(root).get(solver_id, Path(root) / "solvers" / solver_id)


def integration(solver_id):
    if not isinstance(solver_id, str) or not solver_id or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789_" for c in solver_id):
        raise EvaluationError("unsupported_solver", "Use an installed solver integration ID")
    path = integration_folder(solver_id) / "metadata.json"
    if not path.is_file():
        raise EvaluationError("unsupported_solver", f"No integration: {solver_id}")
    metadata = strict_json(path.read_text(encoding="utf-8"))
    if metadata["id"] != solver_id:
        raise EvaluationError("infrastructure_error", "Integration metadata ID mismatch")
    return metadata


def _copied_sources(dockerfile, root):
    """The build-context paths a Dockerfile's COPY and ADD instructions read.

    Sources from another stage (--from) and URLs are not in the context: the
    Dockerfile itself names them, with their checksums.
    """
    lines = []
    for line in dockerfile.read_text(encoding="utf-8").splitlines():
        if lines and lines[-1].endswith("\\"):
            lines[-1] = lines[-1][:-1] + " " + line
        else:
            lines.append(line)
    sources = []
    for line in lines:
        words = line.strip().split(None, 1)
        if len(words) != 2 or words[0].upper() not in ("COPY", "ADD"):
            continue
        rest = words[1].strip()
        arguments = json.loads(rest) if rest.startswith("[") else shlex.split(rest)
        flags = [word for word in arguments if word.startswith("--")]
        if any(flag.startswith("--from") for flag in flags):
            continue
        sources += [word for word in arguments if not word.startswith("--")][:-1]
    paths = set()
    for source in sources:
        if "://" in source:
            continue
        matches = sorted(Path(root).glob(source.lstrip("/"))) if any(c in source for c in "*?[") else [Path(root) / source]
        if not matches or not all(match.exists() for match in matches):
            raise EvaluationError("infrastructure_error", f"{dockerfile} copies {source}, which is not in the repository")
        for match in matches:
            files = [match] if match.is_file() else [path for path in match.rglob("*") if path.is_file()]
            # As .dockerignore: bytecode never reaches an image.
            paths.update(path for path in files if "__pycache__" not in path.parts and path.suffix != ".pyc")
    # By parts, as POSIX sorts paths: a Windows path compares case-insensitively.
    return sorted(paths, key=lambda path: path.parts)


def recipe(solver_id, root=ROOT):
    """A digest of what an integration's image is built from, the same on every machine.

    It covers the platform, the Dockerfile (which pins base images by digest and
    downloads by checksum) and every repository file the Dockerfile copies in. A
    Docker image ID cannot stand in for it: an image rebuilt from the same files
    gets a new ID, on another machine or on this one.
    """
    dockerfile = integration_folder(solver_id, root) / "Dockerfile"
    if not dockerfile.is_file():
        raise EvaluationError("infrastructure_error", f"No Dockerfile for integration {solver_id}")
    digest = hashlib.sha256(f"platform {PLATFORM}\n".encode())
    for path in [dockerfile, *_copied_sources(dockerfile, root)]:
        relative = path.resolve().relative_to(Path(root).resolve()).as_posix()
        digest.update(f"{relative} {hashlib.sha256(path.read_bytes()).hexdigest()}\n".encode())
    return "sha256:" + digest.hexdigest()


def _engine():
    from .engine import current
    return current()


def image_identity(metadata):
    """The local image's identity. It names the bytes run on this machine only; see recipe."""
    return _engine().image_identity(metadata)


def image_recipe(metadata):
    """The recipe digest evaluation.build stamped on the local image, or None if it has none."""
    return _engine().image_recipe(metadata)


def container_engine():
    """What runs the containers here, recorded with each result: the engine, its version,
    and how it enforces the CPU limit ("quota", or "cores"; see evaluation.engine)."""
    return _engine().describe()


def execute(model_path, instance, metadata, image, *, solution_limit, execution_timeout,
            compilation_timeout, memory_mb, cpus, legacy=False, model_bytes=None, outputs=None):
    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="dcp_candidate_") as temp:
        staging = Path(temp)
        # tempfile directories are 0700 on Linux; the unprivileged container must
        # be able to traverse this dedicated directory (never its host parent).
        staging.chmod(0o755)
        # Only the entrypoint is copied. Never mount its parent (which may contain references/secrets).
        (staging / ("model" + metadata["extension"])).write_bytes(
            Path(model_path).read_bytes() if model_bytes is None else model_bytes)
        # The declared output names, so a runner can map its own naming back to
        # them. They are already in the brief the modeller works from, so this
        # tells a submission nothing it should not know, and never a solution.
        request = {"instance": instance, "solution_limit": solution_limit,
                   "execution_timeout": execution_timeout, "compilation_timeout": compilation_timeout,
                   "legacy": legacy, "outputs": list(outputs or [])}
        (staging / "request.json").write_text(json.dumps(request, allow_nan=False), encoding="utf-8")
        for path in staging.iterdir():
            path.chmod(0o644)
        budget = execution_timeout + (compilation_timeout if metadata.get("compilation", False) else 0) + 10
        from . import licences
        # The licence is bound read-only for this run only, and what the run printed is
        # redacted before anything reads it: the submission can read the licence too.
        with licences.supply(metadata) as licence:
            run = _engine().run(metadata, image, staging, memory_mb=memory_mb, cpus=cpus, timeout=budget,
                                licence=licence)
        code, stdout, stderr = run.code, run.stdout, run.stderr
        if licence is not None:
            stdout, stderr = licence.redact(stdout), licence.redact(stderr)
        if code and licences.licence_error(metadata, licences.failure_message(stderr)):
            raise EvaluationError("licence_unavailable", f"The solver refused its licence: {stderr[-4000:]}")
        if code:
            exited = f"exited {code}" + (f" ({run.readings})" if run.readings else "")
            if run.oom_killed:
                raise EvaluationError("memory_limit", f"The kernel killed a process at the {memory_mb} MB "
                                                      f"memory limit and the runner {exited}: {stderr[-4000:]}")
            raise EvaluationError("execution_error", f"Runner {exited}: {stderr[-4000:]}")
        try:
            records = [strict_json(line) for line in stdout.splitlines() if line.strip()]
        except (ValueError, TypeError, RecursionError) as e:
            raise EvaluationError("invalid_output", f"Malformed runner JSON: {e}") from e
        return records, {"execution_wall_seconds": time.perf_counter() - started, "stderr": stderr[-4000:],
                         "oom_killed": run.oom_killed}


def incumbents(records):
    """The improving solutions a runner reported during an optimisation search, as [seconds, objective]: its
    `incumbent` records (seconds since the search started), in order. They are evidence for an anytime
    measure, never a result: the evaluator checks their shape and otherwise ignores them."""
    found = []
    for x in records:
        if not isinstance(x, dict) or x.get("type") != "incumbent":
            continue
        objective, seconds = x.get("objective"), x.get("seconds")
        if (not isinstance(objective, int) or isinstance(objective, bool) or not isinstance(seconds, (int, float))
                or isinstance(seconds, bool) or seconds < 0 or (found and seconds < found[-1][0])):
            raise EvaluationError("invalid_output", "An incumbent record needs an integer objective and "
                                                    "nondecreasing seconds since the search started")
        found.append([seconds, objective])
    return found


# From this protocol version on, every solution record of an optimisation carries its objective.
OBJECTIVE_PROTOCOL = 2


def check_objectives(records, optimum, protocol_version=1):
    """The objective values a runner reported for an optimisation whose solutions the reference accepted as
    optimal: each must be the problem's own value, so the optimum, as the reference states it. A model whose
    objective is scaled, offset or negated, or a runner that passes on the solver's internal value (a MaxSAT
    cost, a negated maximisation), fails here. The improving solutions must improve and end at that optimum.
    Returns the objectives reported with the solutions (None where a runner before OBJECTIVE_PROTOCOL gave none)."""
    reported = []
    for x in records:
        if not isinstance(x, dict) or x.get("type") != "solution":
            continue
        value = x.get("objective")
        if value is None and protocol_version < OBJECTIVE_PROTOCOL:
            reported.append(None)
            continue
        if not isinstance(value, int) or isinstance(value, bool):
            raise EvaluationError("invalid_output", "A solution record of an optimisation needs its integer objective")
        if value != optimum:
            raise EvaluationError("objective_mismatch", f"The runner reported objective {value} for a solution the "
                                  f"reference accepts as optimal, whose objective is {optimum}: the model's objective "
                                  "must be the problem's own value, without scaling, offset or change of sign")
        reported.append(value)
    found = [objective for _, objective in incumbents(records)]
    if found:
        falling, rising = (all(b < a for a, b in zip(found, found[1:])), all(b > a for a, b in zip(found, found[1:])))
        if found[-1] != optimum or not (falling or rising):
            raise EvaluationError("objective_mismatch", f"The improving solutions reported {found[:3]}"
                                  f"{' ... ' + str(found[-1]) if len(found) > 3 else ''}; they must improve and end "
                                  f"at the optimum, {optimum}, in the problem's own objective")
    return reported


def validate_records(records):
    if not records or not all(isinstance(x, dict) for x in records):
        raise EvaluationError("invalid_output", "Expected runner JSON records")
    incumbents(records)  # their shape; they may come anywhere before the status
    records = [x for x in records if x.get("type") != "incumbent"]
    if not records:
        raise EvaluationError("invalid_output", "Expected runner JSON records")
    if records[-1].get("type") != "status" or any(x.get("type") != "solution" for x in records[:-1]):
        raise EvaluationError("invalid_output", "Expected solution records followed by exactly one status")
    status = records[-1]
    if status.get("status") not in ("complete", "limit", "timeout", "unsat", "error", "unsupported", "compilation_error"):
        raise EvaluationError("invalid_output", "Unknown runner status")
    return [x.get("values") for x in records[:-1]], status
