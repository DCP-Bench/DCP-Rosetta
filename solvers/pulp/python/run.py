"""Runner protocol for the pulp_cbc integration. Runs inside the image only.

A submission defines `create_model(instance)` (`build` in models retained earlier)
returning `(problem, outputs)`, where `problem` is a `pulp.LpProblem`. Its own
`objective` says whether this is an optimization: PuLP leaves it `None` until
something is added to it, and its `sense` says which direction, so the submission
needs no extra convention.

Two things about CBC shape this runner.

CBC reports `status == LpStatusOptimal` even when it stopped on the time limit;
only `sol_status` separates a proven optimum (`LpSolutionOptimal`) from a
feasible point it never proved (`LpSolutionIntegerFeasible`). Reporting the
second as success would let an unproven optimum pass, so every solve here is
judged on `sol_status`.

A MIP solver also returns one solution rather than a stream, so enumeration is
done by excluding what was already found: the objective is pinned to the proven
optimum and each further solve adds a no-good cut over the integer variables the
declared outputs are built from. That needs those variables to be integral and
bounded, and says so explicitly when they are not.
"""
import contextlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import signal
import sys
import tempfile
import threading
import time

sys.path.insert(0, "/opt/runner")
from runtime import emit  # noqa: E402
from runtime import finish as runtime_finish  # noqa: E402

import pulp  # noqa: E402
STARTED = time.monotonic()  # the runner's own clock (benchmarking): read_seconds and main_seconds count from here

INPUT = Path("/input")
# The runner protocol's stream, kept before any redirection of sys.stdout.
PROTOCOL = sys.stdout
# CBC returns floats; a declared output has to be an integer, and anything
# further from one than this is a modelling error rather than solver noise.
TOLERANCE = 1e-6
# How often the optimisation solve's log is read for incumbents.
POLL_SECONDS = 0.05


def leaves(value):
    """Every declared output value, with PuLP's own containers left whole.

    `LpAffineExpression` is a dict of variable to coefficient, so the shared
    `flatten` would walk into an expression and return its coefficients. Both
    PuLP types are leaves here.
    """
    if isinstance(value, (pulp.LpVariable, pulp.LpAffineExpression)):
        return [value]
    if isinstance(value, dict):
        return [x for v in value.values() for x in leaves(v)]
    if isinstance(value, (list, tuple)):
        return [x for v in value for x in leaves(v)]
    return [value]


def resolved(value, read_one):
    """The declared outputs with every leaf replaced by its integer value."""
    if isinstance(value, (pulp.LpVariable, pulp.LpAffineExpression)):
        return read_one(value)
    if isinstance(value, dict):
        return {k: resolved(v, read_one) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [resolved(v, read_one) for v in value]
    return read_one(value)


def load(instance):
    spec = importlib.util.spec_from_file_location("candidate", str(INPUT / "model.py"))
    module = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(sys.stderr):
        spec.loader.exec_module(module)
        create_model = getattr(module, "create_model", None) or module.build
        returned = create_model(instance)
    if not isinstance(returned, tuple) or len(returned) != 2:
        raise ValueError("create_model(instance) must return (problem, outputs)")
    problem, outputs = returned
    if not isinstance(problem, pulp.LpProblem):
        raise ValueError("create_model(instance) must return a pulp.LpProblem")
    if not isinstance(outputs, dict) or not outputs:
        raise ValueError("create_model(instance) must return a nonempty output dictionary")
    return problem, outputs


def read(expression):
    """One declared output value: an integer, never a float from the solver."""
    if isinstance(expression, bool):
        return expression
    value = expression if isinstance(expression, int) else pulp.value(expression)
    if value is None:
        raise ValueError("A declared output has no value; every output must be "
                         "a variable or expression the model constrains")
    rounded = round(value)
    if abs(value - rounded) > TOLERANCE:
        raise ValueError("Declared outputs must be integer valued; no coercion from "
                         f"fractional values (got {value})")
    return int(rounded)


def cut_variables(outputs):
    """The variables a no-good cut has to move, with their bounds."""
    collected = {}
    for leaf in leaves(outputs):
        if isinstance(leaf, pulp.LpVariable):
            found = [leaf]
        elif isinstance(leaf, pulp.LpAffineExpression):
            found = list(leaf.keys())
        else:
            found = []
        for variable in found:
            collected[variable.name] = variable
    return list(collected.values())


def enumerable(variables):
    """Why these variables cannot carry a no-good cut, or None if they can."""
    for variable in variables:
        if variable.cat == pulp.LpContinuous:
            return (f"Enumeration needs integer declared outputs; {variable.name} is continuous")
        if variable.lowBound is None or variable.upBound is None:
            return (f"Enumeration needs bounded declared outputs; {variable.name} has no "
                    "finite lower and upper bound")
    return None


def forbid(problem, variables, index):
    """Forbid the assignment the variables currently hold."""
    indicators = []
    for position, variable in enumerate(variables):
        value = round(pulp.value(variable))
        low, high = int(variable.lowBound), int(variable.upBound)
        if value > low:
            below = pulp.LpVariable(f"_below_{index}_{position}", cat=pulp.LpBinary)
            problem += variable <= value - 1 + (high - value + 1) * (1 - below)
            indicators.append(below)
        if value < high:
            above = pulp.LpVariable(f"_above_{index}_{position}", cat=pulp.LpBinary)
            problem += variable >= value + 1 - (value + 1 - low) * (1 - above)
            indicators.append(above)
    if not indicators:
        # Every declared variable is pinned to its only value: nothing else exists.
        return False
    problem += pulp.lpSum(indicators) >= 1
    return True


class Incumbents:
    """Reports the improving solutions CBC logs during the optimisation solve, as incumbents.

    The solve is the same CBC command; only its log, which msg=0 sends to /dev/null, goes
    to a file (PuLP's logPath) that a thread follows, with CBC's stdout line-buffered
    (coreutils' libstdbuf, as `stdbuf -oL` does) so that each line arrives as it is
    printed. CBC prints `Cbc0012I Integer solution of V found by ...` (also Cbc0004I,
    Cbc0016I) for each new incumbent. V is CBC's internal objective: it minimises, so a
    maximisation shows the negated value, and PuLP keeps the objective's constant to
    itself, so the model's objective is (-V if maximising else V) + constant. A value no
    better than the last one (CBC repeats an incumbent when it restarts) is skipped. The
    seconds count from the call to `solve`.
    """

    LINE = re.compile(rb"^Cbc\d{4}I Integer solution of (\S+) found")
    LIBSTDBUF = "/usr/libexec/coreutils/libstdbuf.so"

    def __init__(self, problem, directory):
        self.sign = -1 if problem.sense == pulp.LpMaximize else 1
        self.constant = problem.objective.constant
        self.path = os.path.join(directory, "cbc.log")
        self.best = None
        self.last = None
        self.start = time.monotonic()
        self.done = threading.Event()
        self.thread = threading.Thread(target=self.follow, daemon=True)

    def follow(self):
        with open(self.path, "rb") as log:
            while True:
                done = self.done.is_set()
                self.read(log)
                if done:
                    return
                self.done.wait(POLL_SECONDS)

    def read(self, log):
        while True:
            offset = log.tell()
            line = log.readline()
            if not line.endswith(b"\n"):
                log.seek(offset)  # not yet complete: read again next time
                return
            found = self.LINE.match(line)
            if not found:
                continue
            try:
                value = float(found.group(1))
            except ValueError:
                continue
            if self.best is not None and value >= self.best:
                continue
            self.best = value
            self.report(self.sign * value + self.constant)

    def report(self, objective):
        rounded = round(objective)
        if abs(objective - rounded) > TOLERANCE:
            return  # not an integer objective value
        self.last = int(rounded)
        # The solve runs with sys.stdout redirected to stderr, so the record goes to the protocol stream itself.
        print(json.dumps({"type": "incumbent", "objective": self.last, "seconds": time.monotonic() - self.start}),
              file=PROTOCOL, flush=True)

    @contextlib.contextmanager
    def following(self):
        open(self.path, "w").close()
        saved = {key: os.environ.get(key) for key in ("LD_PRELOAD", "_STDBUF_O")}
        os.environ.update(LD_PRELOAD=self.LIBSTDBUF, _STDBUF_O="L")
        self.thread.start()
        try:
            yield self.path
        finally:
            for key, value in saved.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
            self.done.set()
            self.thread.join()

    def proven(self, problem):
        """CBC logs no incumbent for a model its preprocessing solves outright: the proven
        optimum is then reported when the solve returns, as the last incumbent."""
        objective = pulp.value(problem.objective)
        if objective is not None and (self.last is None or round(objective) != self.last):
            self.report(objective)


def attempt(problem, deadline, incumbents=False):
    """Solve once inside the remaining budget; say what CBC actually concluded. With
    `incumbents`, the optimisation solve's improving solutions are reported as found."""
    left = deadline - time.monotonic()
    if left <= 0:
        return "timeout"
    if incumbents:
        directory = tempfile.mkdtemp(prefix="cbc_")
        follower = Incumbents(problem, directory)
        try:
            with follower.following() as log:
                solver = pulp.PULP_CBC_CMD(msg=0, threads=1, timeLimit=max(1, int(left)), logPath=log)
                with contextlib.redirect_stdout(sys.stderr):
                    problem.solve(solver)
        finally:
            shutil.rmtree(directory, ignore_errors=True)
        if problem.sol_status == pulp.LpSolutionOptimal:
            follower.proven(problem)
    else:
        solver = pulp.PULP_CBC_CMD(msg=0, threads=1, timeLimit=max(1, int(left)))
        with contextlib.redirect_stdout(sys.stderr):
            problem.solve(solver)
    if problem.status == pulp.LpStatusInfeasible:
        return "infeasible"
    if problem.status == pulp.LpStatusUnbounded:
        return "unbounded"
    # CBC says Optimal when it stopped on time, so sol_status is the one to read.
    if problem.sol_status != pulp.LpSolutionOptimal:
        return "timeout"
    return "solved"


def register(problem, variables):
    """Make sure every declared output variable reaches the solver.

    PuLP only writes out the variables its objective and constraints mention, so
    an output no constraint touches would come back without a value. A bound it
    already has is enough to put it in the program.
    """
    known = {variable.name for variable in problem.variables()}
    for variable in variables:
        if variable.name in known:
            continue
        if variable.lowBound is not None:
            problem += variable >= variable.lowBound
        elif variable.upBound is not None:
            problem += variable <= variable.upBound
        else:
            raise ValueError(f"Declared output {variable.name} is in no constraint and has "
                             "no bound, so the solver would never give it a value")


# Seconds the submission took to build the model (the LpProblem; PuLP hands it to CBC inside solve), and from STARTED until the
# request was read, for benchmarking.
BUILD_SECONDS = 0.0
READ_SECONDS = 0.0


def finish(status, detail="", **metadata):
    runtime_finish(status, detail, build_seconds=BUILD_SECONDS, read_seconds=READ_SECONDS,
                   main_seconds=time.monotonic() - STARTED, **metadata)


def solve(request):
    global BUILD_SECONDS
    deadline = time.monotonic() + request["execution_timeout"]
    building = time.monotonic()
    problem, outputs = load(request["instance"])
    optimizing = problem.objective is not None
    register(problem, cut_variables(outputs))
    BUILD_SECONDS = time.monotonic() - building

    verdict = attempt(problem, deadline, incumbents=optimizing)
    if verdict == "infeasible":
        return finish("unsat")
    if verdict == "unbounded":
        return finish("error", "The objective is unbounded")
    if verdict != "solved":
        return finish("timeout", "Candidate optimum was not proven" if optimizing else "")

    limit = request["solution_limit"]
    variables = cut_variables(outputs)
    if limit > 1:
        obstacle = enumerable(variables)
        if obstacle is not None:
            return finish("unsupported", obstacle)
        if optimizing:
            # Only assignments that achieve the proven optimum may be enumerated.
            best = pulp.value(problem.objective)
            problem += problem.objective <= best + TOLERANCE
            problem += problem.objective >= best - TOLERANCE

    seen, count, index = set(), 0, 0
    while True:
        values = resolved(outputs, read)
        key = json.dumps(values, sort_keys=True)
        if key not in seen:
            seen.add(key)
            emit({"type": "solution", "values": values})
            count += 1
            if count >= limit:
                return finish("limit")
        if not forbid(problem, variables, index):
            return finish("complete")
        index += 1
        verdict = attempt(problem, deadline)
        if verdict == "infeasible":
            return finish("complete")
        if verdict != "solved":
            return finish("timeout")


def main():
    try:
        global READ_SECONDS
        request = json.loads((INPUT / "request.json").read_text())
        READ_SECONDS = time.monotonic() - STARTED
        if request.get("legacy"):
            return finish("unsupported", "Legacy submissions are not supported by pulp_cbc")

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
