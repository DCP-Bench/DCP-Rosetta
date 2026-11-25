"""Runner protocol for the groundfox_fox integration. Runs inside the image only.

A submission is a Python file holding a FOX theory (`FOX`) and a function
`structure(instance)` that interprets its input symbols from the instance. The
runner writes the structure, grounds the whole with `groundfox` into DIMACS CNF
(with a CertiFOX proof log, which checkfox must accept before anything is solved), solves it with CaDiCaL 3.0.0 through
python-sat, and reads each declared output back from the out-predicate of the same
name: index positions first, value last (`dcp_fox.py`). Further solutions are found
by blocking the current assignment of the output atoms. FOX has no objective, so
every problem is solved as a satisfaction problem.
"""
import contextlib
import json
from pathlib import Path
import signal
import sys
import tempfile
import time

sys.path.insert(0, "/opt/runner")
import dcp_fox  # noqa: E402
from runtime import emit  # noqa: E402
from runtime import finish as runtime_finish  # noqa: E402

STARTED = time.monotonic()
INPUT = Path("/input")
BUILD_SECONDS = 0.0
READ_SECONDS = 0.0
PROOF = {}  # proof verdict, grounding size and timings, reported with the final status


def finish(status, detail="", **metadata):
    runtime_finish(status, detail, build_seconds=BUILD_SECONDS, read_seconds=READ_SECONDS,
                   main_seconds=time.monotonic() - STARTED, **PROOF, **metadata)


def tmp_full():
    """The CNF and proof log live in the 512 MiB /tmp; a grounding that fills it is a resource limit."""
    import shutil
    return shutil.disk_usage("/tmp").free < 16 * 1024 * 1024


TMP_FULL = "the grounding filled /tmp (CNF and proof log), a resource limit like memory"


def solve(request):
    global BUILD_SECONDS
    deadline = time.monotonic() + request["execution_timeout"]
    names = list(request.get("outputs") or [])
    building = time.monotonic()
    with contextlib.redirect_stdout(sys.stderr):
        fox, structure, flags = dcp_fox.load(INPUT / "model.py")
        outputs = dcp_fox.check_outputs(fox, names)
        text = fox + "\n" + dcp_fox.structure_text(fox, structure(request["instance"]))
    with tempfile.TemporaryDirectory(dir="/tmp") as work:
        try:
            cnf, atoms, clauses = dcp_fox.ground(text, flags, work, max(deadline - time.monotonic(), 0.1))
        except dcp_fox.subprocess.TimeoutExpired:
            return finish("timeout", "groundfox did not finish within the time limit")
        except dcp_fox.ModelError:
            if tmp_full():
                return finish("timeout", TMP_FULL)
            raise
        PROOF["ground_seconds"] = round(time.monotonic() - building, 3)
        PROOF["cnf_clauses"] = clauses
        # The grounding is only trusted once checkfox accepts its proof log.
        checking = time.monotonic()
        try:
            verdict, message = dcp_fox.check_proof(flags, work, max(deadline - time.monotonic(), 0.1))
        except dcp_fox.subprocess.TimeoutExpired:
            return finish("timeout", "checkfox did not finish checking the grounding proof within the time limit")
        PROOF["proof_seconds"] = round(time.monotonic() - checking, 3)
        PROOF["proof"] = verdict
        if verdict != "valid":
            if tmp_full():
                return finish("timeout", TMP_FULL)
            return finish("error", f"checkfox {verdict} the GroundFOX proof of this grounding: {message}")
        solver = dcp_fox.Solver(cnf)  # its process loads the CNF before the folder goes
    found = dcp_fox.output_atoms(atoms, names, outputs)
    variables = sorted({v for entries in found.values() for v, _, _ in entries})
    BUILD_SECONDS = time.monotonic() - building
    seen, count = set(), 0
    while count < request["solution_limit"]:
        left = deadline - time.monotonic()
        if left <= 0:
            return finish("timeout")
        result = solver.solve(left)
        if result is None:
            return finish("timeout")
        if not result:
            return finish("complete" if count else "unsat")
        truth = solver.true_vars()
        values = dcp_fox.decode(truth, found)
        if not variables:
            raise dcp_fox.ModelError("No output atom occurs in the grounding")
        solver.block(truth, variables)
        key = json.dumps(values, sort_keys=True)
        if key not in seen:
            seen.add(key)
            emit({"type": "solution", "values": values})
            count += 1
    finish("limit")


def main():
    try:
        global READ_SECONDS
        request = json.loads((INPUT / "request.json").read_text())
        READ_SECONDS = time.monotonic() - STARTED
        if request.get("legacy"):
            return finish("unsupported", "Legacy submissions are not supported by groundfox_fox")

        def expired(signum, frame):
            raise TimeoutError("Runner execution budget exceeded")

        signal.signal(signal.SIGALRM, expired)
        signal.setitimer(signal.ITIMER_REAL, request["execution_timeout"] + 5)
        solve(request)
    except TimeoutError:
        finish("timeout")
    except Exception as error:
        import traceback
        traceback.print_exc(file=sys.stderr)
        finish("error", str(error))


if __name__ == "__main__":
    main()
