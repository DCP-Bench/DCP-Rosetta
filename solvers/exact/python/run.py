"""Runner protocol for the exact integration. Runs inside the image only.

A submission defines `create_model(instance)` returning `(solver, outputs)`, with
`solver` an `exact.Exact`. An optimisation problem sets its objective on the solver
with `solver.setObjective(terms, minimize=...)`, as Exact's own examples do. Exact
cannot hand an objective back, so the runner replaces `exact.Exact` with a subclass
that records the arguments of `setObjective` before the submission is imported; it
needs the terms to pin the optimum while enumerating. Models retained before
2026-11-02 define `build(instance)` and may return the objective as a third value,
`(direction, terms)` with direction "minimize" or "maximize"; that form still works.

Exact identifies variables by name, so `outputs` maps each declared output name
to variable names, or nested lists of them. Values come back as integers; the
evaluator compares a 0/1 integer and a Boolean as equal, so a variable declared
over 0..1 satisfies a Boolean output without any special handling.

Three things about this solver decide how the runner is written:

* `toOptimum` answers **`"SAT"`** when it proved the optimum. There is no
  `"OPTIMAL"`. `"TIMEOUT"` means the search stopped short.
* `hasSolution()` stays true after `"TIMEOUT"` and after `"UNSAT"`, so it is
  never the test for whether there is an answer. The returned state is.
* Exact minimises internally, so a maximisation's optimum comes back negated.

Incumbents. `toOptimum` runs its whole optimisation loop in C++, holding the GIL, and has
no callback; the only trace of its improving solutions is the log it writes to fd 1 at
`verbosity` 1: a line `c     bounds UB >= LB @ SECONDS, CONFLICTS` each time a bound
moves, UB being the best solution's value on Exact's internal scale. So the model runs in
a worker process whose stdout (Exact's log and the worker's protocol records, line by
line) the supervisor reads as it comes: lines starting `c ` are Exact's (all its lines
do), anything else the worker or the submission writes is relayed unchanged. Inside `toOptimum` that internal value is the
minimised objective (the problem's value, negated for a maximisation) plus
`1 + sum(|coefficient| * (ub - lb))` over the objective's terms (the weight of the flag
variable `toOptimum` adds, Exact's interface/IntProg.cpp); the worker tells the
supervisor that weight and the objective's range before the search, and the optimum
after it. The supervisor reports each strictly better value within that range as an
`incumbent`, with Exact's own SECONDS (since `toOptimum` started), and ends with the
proven optimum if the log did not. Everything else Exact prints goes to stderr. Verbosity
only adds this log; the search is the one `toOptimum` always ran.
"""
import contextlib
import importlib.util
import json
from pathlib import Path
import re
import signal
import subprocess
import sys
import threading
import time

sys.path.insert(0, "/opt/runner")
from runtime import emit, flatten, mapped  # noqa: E402
from runtime import finish as runtime_finish  # noqa: E402

WORKER = "--worker" in sys.argv
if WORKER:
    import ctypes
    # Exact writes its log through std::cout, synchronised with C's stdout, which is fully buffered on a
    # pipe: lines would reach the supervisor late and cut at buffer boundaries, between the worker's own
    # records. Line buffering hands over each line whole, as it is written.
    LIBC = ctypes.CDLL(None)
    LIBC.setvbuf(ctypes.c_void_p.in_dll(LIBC, "stdout"), None, 1, 0)  # _IOLBF
    import exact  # noqa: E402
STARTED = time.monotonic()  # the runner's own clock (benchmarking): read_seconds and main_seconds count from here

DIRECTIONS = ("minimize", "maximize")
# Seconds the supervisor allows the worker beyond the execution budget before it kills it.
GRACE = 5
# Exact's log line for a bound change (verbosity 1): "c     bounds UB >= LB @ SECONDS, CONFLICTS".
BOUNDS = re.compile(r"^c\s+bounds\s+(-?\d+)\s+>=\s+(-?\d+)\s+@\s+([0-9.eE+-]+)")
# The worker's private records to the supervisor, never relayed.
SCALE, SEARCHED = "_exact_scale", "_exact_searched"


if WORKER:
    class Exact(exact.Exact):
        """An exact.Exact that remembers the objective set on it and its variables' bounds, and logs its
        bounds (verbosity 1) for the supervisor to read incumbents from."""

        objective = None  # (terms, minimize, offset) once setObjective was called

        def __init__(self, options=()):
            options = [(str(name), str(value)) for name, value in options if name != "verbosity"]
            super().__init__(options + [("verbosity", "1")])
            self.bounds = {}

        def addVariable(self, name, lower_bound=0, upper_bound=1, *args, **kwargs):
            super().addVariable(name, lower_bound, upper_bound, *args, **kwargs)
            self.bounds[name] = (int(lower_bound), int(upper_bound))

        def setObjective(self, terms, minimize=True, offset=0):
            terms = list(terms)
            super().setObjective(terms, minimize, offset)
            self.objective = (terms, minimize, offset)

    exact.Exact = Exact  # what `from exact import Exact` gives the submission


def load(instance):
    """Import the submission and normalise what it returned."""
    spec = importlib.util.spec_from_file_location("candidate", "/input/model.py")
    module = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(sys.stderr):
        spec.loader.exec_module(module)
        create_model = getattr(module, "create_model", None) or module.build
        returned = create_model(instance)
    if not isinstance(returned, tuple) or len(returned) not in (2, 3):
        raise ValueError("create_model(instance) must return (solver, outputs)")
    solver, outputs = returned[0], returned[1]
    objective = returned[2] if len(returned) == 3 else None
    if not isinstance(solver, Exact):
        raise ValueError("the first value must be an exact.Exact")
    if not isinstance(outputs, dict) or not outputs:
        raise ValueError("create_model(instance) must return a nonempty output dictionary")
    for leaf in flatten(outputs):
        if not isinstance(leaf, str):
            raise ValueError("an output leaf must be a variable name; got "
                             f"{type(leaf).__name__}")
    if objective is not None:
        if (not isinstance(objective, (tuple, list)) or len(objective) != 2
                or objective[0] not in DIRECTIONS):
            raise ValueError('the objective must be ("minimize", terms) or '
                             '("maximize", terms), with terms a list of '
                             "(coefficient, variable name) pairs")
    return solver, outputs, objective


# Seconds the submission took to build the model (posting into Exact, its objective included),
# and from STARTED until the request was read, for benchmarking.
BUILD_SECONDS = 0.0
READ_SECONDS = 0.0


def finish(status, detail="", **metadata):
    runtime_finish(status, detail, build_seconds=BUILD_SECONDS, read_seconds=READ_SECONDS,
                   main_seconds=time.monotonic() - STARTED, **metadata)


def objective_value(solver):
    """The model's objective on the last solution, in the problem's terms: its terms evaluated on the
    solution, plus the offset. (Exact's own value, from toOptimum, is negated for a maximisation.)"""
    terms, _minimise, offset = solver.objective
    variables = sorted({name for _, name in terms})
    values = dict(zip(variables, solver.getLastSolutionFor(variables)))
    return int(offset + sum(coefficient * values[name] for coefficient, name in terms))


def scale(solver):
    """What the supervisor needs to read the log of toOptimum: the flag's weight, the direction, and the
    range of the problem's objective value (offset + terms) over the variables' bounds."""
    terms, minimise, offset = solver.objective
    weight, low, high = 1, offset, offset
    for coefficient, name in terms:
        lb, ub = solver.bounds[name]
        weight += abs(coefficient) * (ub - lb)
        low += min(coefficient * lb, coefficient * ub)
        high += max(coefficient * lb, coefficient * ub)
    return {"type": SCALE, "weight": weight, "minimize": bool(minimise), "low": low, "high": high}


def worker_main():
    global BUILD_SECONDS, READ_SECONDS
    request = json.loads(Path("/input/request.json").read_text())
    READ_SECONDS = time.monotonic() - STARTED

    started = time.monotonic()
    deadline = started + request["execution_timeout"]
    building = time.monotonic()
    solver, outputs, objective = load(request["instance"])
    if objective is not None:
        direction, terms = objective
        solver.setObjective(terms, minimize=direction == "minimize")
    BUILD_SECONDS = time.monotonic() - building
    names = flatten(outputs)

    if solver.objective is not None:
        terms, minimise, offset = solver.objective
        left = deadline - time.monotonic()
        if left <= 0:
            return finish("timeout", "the budget ran out before the search began",
                          solve_seconds=time.monotonic() - started)
        if isinstance(solver, Exact) and all(name in solver.bounds for _, name in terms):
            LIBC.fflush(None)
            emit(scale(solver))
        state, value = solver.toOptimum(left)
        spent = time.monotonic() - started
        # The problem's optimum (offset included), with which the supervisor ends the incumbents.
        LIBC.fflush(None)
        emit({"type": SEARCHED, **({"optimum": int(value if minimise else -value)} if state == "SAT" else {})})
        if state == "UNSAT":
            return finish("unsat", solve_seconds=spent)
        if state != "SAT":
            # "TIMEOUT", and anything else, means the optimum was not proven.
            # Exact still holds a solution, which must not be reported as one.
            return finish("timeout", f"the optimum was not proven ({state})",
                          solve_seconds=spent)
        # Exact reports the objective plus its offset, negated when maximising.
        optimum = (value if minimise else -value) - offset
        # Pin the objective so every further solution is an optimal one.
        solver.addConstraint(terms, True, optimum, True, optimum)

    limit = request["solution_limit"]
    emitted = 0
    while emitted < limit:
        left = deadline - time.monotonic()
        if left <= 0:
            return finish("timeout", "the budget ran out before the search finished",
                          solve_seconds=time.monotonic() - started)
        state = solver.runFull(False, left)
        spent = time.monotonic() - started
        if state == "UNSAT":
            return finish("complete" if emitted else "unsat", solve_seconds=spent)
        if state != "SAT":
            return finish("timeout", f"the search did not finish ({state})",
                          solve_seconds=spent)
        values = dict(zip(names, solver.getLastSolutionFor(names)))
        record = {"type": "solution", "values": mapped(outputs, values.__getitem__)}
        if solver.objective is not None:
            record["objective"] = objective_value(solver)
        emit(record)
        emitted += 1
        if emitted >= limit:
            break
        # Exact's own blocking, projected onto the declared outputs, so two
        # answers that differ only in auxiliary variables count as one.
        solver.invalidateLastSol(names)
    finish("limit", solve_seconds=time.monotonic() - started)


class Incumbents:
    """Reads incumbents from Exact's log of toOptimum, as SCALE describes it (see the module docstring)."""

    def __init__(self):
        self.scale, self.done, self.last, self.seconds = None, False, None, 0.0

    def better(self, value):
        if self.last is None:
            return True
        return value < self.last if self.scale["minimize"] else value > self.last

    def report(self, value, seconds):
        self.last, self.seconds = value, max(self.seconds, seconds)
        emit({"type": "incumbent", "objective": value, "seconds": self.seconds})

    def line(self, text):
        """A log line: an incumbent when it is a bound line of the search; False when it is not one."""
        match = BOUNDS.match(text)
        if match is None or self.scale is None:
            return False
        if self.done:
            return True
        internal = int(match.group(1)) - self.scale["weight"]
        value = internal if self.scale["minimize"] else -internal
        # The first bound is the range's end plus one (no solution yet): outside the range, never a solution.
        if self.scale["low"] <= value <= self.scale["high"] and self.better(value):
            self.report(value, float(match.group(3)))
        return True

    def searched(self, record):
        if self.scale is not None and not self.done and "optimum" in record and self.better(record["optimum"]):
            # Exact's log need not show the last solution: the proven optimum ends the incumbents.
            self.report(record["optimum"], self.seconds)
        self.done = True


def supervise():
    """Run the worker, turn its log into incumbents, relay its records, and decide the single final status."""
    global READ_SECONDS
    request = json.loads(Path("/input/request.json").read_text())
    READ_SECONDS = time.monotonic() - STARTED
    if request.get("legacy"):
        return finish("unsupported", "This integration has no legacy submission format")
    worker = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "--worker"],
                              stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, text=True, bufsize=1)
    expired = threading.Event()

    def kill():
        expired.set()
        worker.kill()

    watchdog = threading.Timer(request["execution_timeout"] + GRACE, kill)
    watchdog.start()
    final, incumbents = None, Incumbents()
    try:
        for line in worker.stdout:
            if line.startswith("c "):  # Exact's log: every line it writes starts so
                if not incumbents.line(line):
                    sys.stderr.write(line)
                continue
            if not line.startswith("{"):  # anything else on stdout is not the runner's: relayed, as before
                sys.stdout.write(line)
                sys.stdout.flush()
                continue
            try:
                record = json.loads(line)
            except ValueError:
                continue  # a line cut short by a kill; the missing final status reports it
            kind = record.get("type")
            if kind == SCALE:
                incumbents.scale = record
            elif kind == SEARCHED:
                incumbents.searched(record)
            elif kind == "status":
                final = line
            else:
                sys.stdout.write(line)
                sys.stdout.flush()
    finally:
        code = worker.wait()
        watchdog.cancel()

    if final is not None and code == 0:
        sys.stdout.write(final)
        sys.stdout.flush()
    elif expired.is_set():
        finish("timeout", "Candidate did not finish within its execution budget")
    elif code < 0:
        finish("error", f"Exact worker terminated by signal {signal.Signals(-code).name}")
    else:
        finish("error", f"Exact worker exited with status {code}" + ("" if final is None else
                                                                     " after its final status"))


if __name__ == "__main__":
    if WORKER:
        try:
            worker_main()
        except Exception as error:
            import traceback
            traceback.print_exc(file=sys.stderr)
            finish("error", str(error))
    else:
        try:
            supervise()
        except Exception as error:
            import traceback
            traceback.print_exc(file=sys.stderr)
            finish("error", str(error))
