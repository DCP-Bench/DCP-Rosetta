"""Runner protocol for the cvc5_python integration. Runs inside the image only.

A submission defines `create_model(instance)` returning `(solver, outputs)`: solver is a
`cvc5.pythonic.Solver` holding the constraints. Models retained before 2026-10-30 define
`build(instance)` returning `(constraints, outputs)`, which is still accepted.

The submission uses cvc5's pythonic API (`cvc5.pythonic`). cvc5 has no optimiser, so this
integration is satisfaction-only: it takes no objective. The runner enumerates distinct
declared outputs by blocking.
"""
import contextlib
import importlib.util
import json
from pathlib import Path
import signal
import sys
import time

sys.path.insert(0, "/opt/runner")
from runtime import emit, flatten, mapped  # noqa: E402
from runtime import finish as runtime_finish  # noqa: E402

import cvc5.pythonic as c5  # noqa: E402
STARTED = time.monotonic()  # the runner's own clock (benchmarking): read_seconds and main_seconds count from here

INPUT = Path("/input")


def load(instance):
    """Import the submission and normalise what it returned. The file is loaded as module
    "candidate", so its `if __name__ == "__main__":` run block never runs."""
    spec = importlib.util.spec_from_file_location("candidate", str(INPUT / "model.py"))
    module = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(sys.stderr):
        spec.loader.exec_module(module)
        create_model = getattr(module, "create_model", None) or module.build
        returned = create_model(instance)
    if not isinstance(returned, tuple) or len(returned) != 2:
        raise ValueError("create_model(instance) must return (solver, outputs); cvc5_python "
                         "is satisfaction-only and takes no objective")
    constraints, outputs = returned
    if not isinstance(outputs, dict) or not outputs:
        raise ValueError("create_model(instance) must return a nonempty output dictionary")
    return assertions(constraints), configuration(constraints), outputs


# Options the runner sets itself: a returned Solver's values for these are not copied.
OWNED = ("incremental", "produce-models", "tlimit", "tlimit-per")


def configuration(constraints):
    """The logic and the user-set options of a returned Solver, as (logic, options).

    The runner solves on fresh solvers, so it reproduces these on each of them.
    A list of constraints, or a Solver that sets nothing, gives (None, {}).
    """
    if not isinstance(constraints, c5.Solver):
        return None, {}
    native = constraints.solver
    logic = native.getLogic() if native.isLogicSet() else None
    options = {name: native.getOption(name) for name in native.getOptionNames()
               if name not in OWNED and native.getOptionInfo(name)["setByUser"]}
    return logic, options


def fresh(configuration):
    """A new pythonic Solver with the returned Solver's logic and options."""
    logic, options = configuration
    solver = c5.Solver() if logic is None else c5.SolverFor(logic)
    for name, value in options.items():
        solver.set(name, value)
    return solver


def assertions(constraints):
    """Accept a cvc5 pythonic Solver, a sequence of constraints, or one constraint."""
    if isinstance(constraints, c5.Solver):
        return list(constraints.assertions())
    if isinstance(constraints, (list, tuple)):
        return list(constraints)
    return [constraints]


def read(expression, model):
    """One declared output value: an integer or a Boolean, never a real."""
    if isinstance(expression, bool):
        return expression
    if isinstance(expression, int):
        return expression
    value = model.eval(expression, model_completion=True)
    if c5.is_true(value):
        return True
    if c5.is_false(value):
        return False
    if isinstance(value, c5.IntNumRef):
        return value.as_long()
    raise ValueError("Declared outputs must be integer or Boolean values; no coercion "
                     f"from reals or other sorts (got {value} for {expression})")


def blocking(expressions, model):
    """Forbid this exact assignment of the declared outputs."""
    clause = [expression != model.eval(expression, model_completion=True)
              for expression in expressions if not isinstance(expression, (bool, int))]
    # With only constant outputs there is a single possible assignment, so
    # nothing further exists to find.
    return c5.Or(*clause) if clause else c5.BoolVal(False)


def remaining(deadline):
    left = deadline - time.monotonic()
    return None if left <= 0 else max(1, int(left * 1000))


def check(solver, deadline):
    """One check under the time left: (result, None), or (None, (status, detail)) when out of budget."""
    budget = remaining(deadline)
    if budget is None:
        return None, ("timeout", "")
    # tlimit-per is the limit of one check() call; 0 would mean no limit.
    solver.set("tlimit-per", budget)
    result = solver.check()
    if result == c5.unknown:
        reason = str(solver.reason_unknown())
        if reason.endswith("TIMEOUT"):
            return None, ("timeout", "")
        return None, ("error", f"cvc5 returned unknown: {reason}")
    return result, None


# Seconds the submission took to build the model (its cvc5 terms), and from STARTED until the
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
    constraints, setup, outputs = load(request["instance"])
    BUILD_SECONDS = time.monotonic() - building
    flat = flatten(outputs)

    solver = fresh(setup)
    solver.add(constraints)
    count = 0
    while count < request["solution_limit"]:
        result, failure = check(solver, deadline)
        if failure is not None:
            return finish(failure[0], failure[1])
        if result == c5.unsat:
            return finish("complete" if count else "unsat")
        model = solver.model()
        emit({"type": "solution", "values": mapped(outputs, lambda e: read(e, model))})
        count += 1
        if count == request["solution_limit"]:
            break
        solver.add(blocking(flat, model))
    finish("limit")


def main():
    try:
        global READ_SECONDS
        request = json.loads((INPUT / "request.json").read_text())
        READ_SECONDS = time.monotonic() - STARTED
        if request.get("legacy"):
            return finish("unsupported", "Legacy submissions are not supported by cvc5_python")

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
