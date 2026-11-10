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
"""
import contextlib
import importlib.util
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, "/opt/runner")
from runtime import emit, flatten, mapped  # noqa: E402
from runtime import finish as runtime_finish  # noqa: E402

import exact  # noqa: E402
STARTED = time.monotonic()  # the runner's own clock (benchmarking): read_seconds and main_seconds count from here

DIRECTIONS = ("minimize", "maximize")


class Exact(exact.Exact):
    """An exact.Exact that remembers the objective set on it."""

    objective = None  # (terms, minimize, offset) once setObjective was called

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


def main():
    global BUILD_SECONDS, READ_SECONDS
    request = json.loads(Path("/input/request.json").read_text())
    READ_SECONDS = time.monotonic() - STARTED
    if request.get("legacy"):
        return finish("unsupported", "This integration has no legacy submission format")

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
        state, value = solver.toOptimum(left)
        spent = time.monotonic() - started
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


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        import traceback
        traceback.print_exc(file=sys.stderr)
        finish("error", str(error))
