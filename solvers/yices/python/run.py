"""Runner protocol for the yices_python integration. Runs inside the image only.

A submission defines `build(instance)` returning `(formulas, outputs)`, or
`(formulas, outputs, (direction, objective))` for an optimization problem where
direction is "minimize" or "maximize". Formulas, output leaves and the objective
are Yices term handles built with the `yices` Python bindings. The runner owns
every context: it proves the optimum by tightening the objective until unsat,
pins it in a fresh context, enumerates distinct declared outputs with no-goods,
and never reports success on an unproven optimum.
"""
import importlib.util
import json
import os
from pathlib import Path
import signal
import sys
import time

sys.path.insert(0, "/opt/runner")
from runtime import flatten, mapped  # noqa: E402

from yices import Config, Context, Model, Status, Terms, YicesException  # noqa: E402

INPUT = Path("/input")
DIRECTIONS = ("minimize", "maximize")
# The protocol owns the real stdout; fd 1 is pointed at stderr for the whole run, so
# that C-level prints from libyices and prints from the submission cannot corrupt it.
PROTOCOL = os.fdopen(os.dup(1), "w")
os.dup2(2, 1)
sys.stdout = sys.stderr


def emit(record):
    PROTOCOL.write(json.dumps(record, allow_nan=False) + "\n")
    PROTOCOL.flush()


def finish(status, detail="", **metadata):
    emit({"type": "status", "status": status, "detail": detail, **metadata})


def is_constant(leaf):
    return isinstance(leaf, bool)


def check_term(term, what, kinds):
    """Fail early, with a message that names the problem, on a value that is not a term."""
    if isinstance(term, bool) and kinds == "bool":
        raise ValueError(f"{what} is a Python bool, not a Boolean Yices term; Python comparisons "
                         "such as x > 3 do not build terms, use Terms.arith_gt_atom and friends")
    if isinstance(term, bool) or not isinstance(term, int):
        raise ValueError(f"{what} must be a Yices term (an int handle), got {type(term).__name__} "
                         f"{term!r}; build constants with Terms.integer / Terms.true()")
    if kinds == "bool" and not Terms.is_bool(term):
        raise ValueError(f"{what} must be a Boolean term; Python comparisons such as x > 3 do "
                         "not build terms, use Terms.arith_gt_atom and friends")
    if kinds == "int" and not Terms.is_int(term):
        raise ValueError(f"{what} must be an integer term")
    if kinds == "leaf" and not (Terms.is_bool(term) or Terms.is_int(term)):
        raise ValueError(f"{what} must be an integer or Boolean term; no coercion from reals "
                         "or other types")


def load(instance):
    """Import the submission and normalise what it returned."""
    spec = importlib.util.spec_from_file_location("candidate", str(INPUT / "model.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    returned = module.build(instance)
    if not isinstance(returned, tuple) or len(returned) not in (2, 3):
        raise ValueError("build(instance) must return (formulas, outputs) or "
                         "(formulas, outputs, (direction, objective))")
    formulas, outputs = returned[0], returned[1]
    if isinstance(formulas, int) and not isinstance(formulas, bool):
        formulas = [formulas]
    if not isinstance(formulas, (list, tuple)):
        raise ValueError("formulas must be a list of Boolean Yices terms")
    for index, formula in enumerate(formulas):
        check_term(formula, f"formulas[{index}]", "bool")
    if not isinstance(outputs, dict) or not outputs:
        raise ValueError("build(instance) must return a nonempty output dictionary")
    for leaf in flatten(outputs):
        if not is_constant(leaf):
            check_term(leaf, "an output leaf", "leaf")
    objective = returned[2] if len(returned) == 3 else None
    if objective is not None:
        if (not isinstance(objective, (tuple, list)) or len(objective) != 2
                or objective[0] not in DIRECTIONS):
            raise ValueError('The objective must be ("minimize", term) or ("maximize", term)')
        check_term(objective[1], "the objective", "int")
    logic = getattr(module, "LOGIC", None)
    if logic is not None and not isinstance(logic, str):
        raise ValueError("LOGIC must be a string such as 'QF_NIA'")
    return list(formulas), logic, outputs, objective


def fresh(formulas, logic):
    """A new context over the formulas, in the logic the submission asked for (or the default)."""
    if logic is None:
        context = Context()
    else:
        config = Config()
        config.default_config_for_logic(logic)
        context = Context(config)
        config.dispose()
    if formulas:
        context.assert_formulas(formulas)
    return context


def remaining(deadline):
    left = deadline - time.monotonic()
    return None if left <= 0 else left


def check(context, deadline):
    """One check under the time left: (status, None), or (None, (status, detail))."""
    left = remaining(deadline)
    if left is None:
        return None, ("timeout", "")
    status = context.check_context(timeout=left)
    if status in (Status.SAT, Status.UNSAT):
        return status, None
    if status == Status.INTERRUPTED:
        return None, ("timeout", "")
    if status == Status.UNKNOWN:
        if time.monotonic() >= deadline:
            return None, ("timeout", "")
        return None, ("error", "yices returned unknown")
    return None, ("error", f"yices returned status {status}")


def number(model, term):
    """Read an integer or Boolean value; anything else is a loud error."""
    value = model.get_value(term)
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    raise ValueError("Declared outputs must be integer or Boolean values that fit in 64 bits; "
                     f"got {value!r} for term {term}")


def read(leaf, model):
    return leaf if is_constant(leaf) else number(model, leaf)


def optimum(formulas, logic, direction, objective, deadline):
    """Prove the optimal objective value, or say why it could not be proven.

    Each step asserts a strictly better objective permanently on one context. The last
    model found is the optimum once the next step is unsat; unknown, interruption or
    running out of time before that is `timeout`.
    """
    context = fresh(formulas, logic)
    best = None
    try:
        while True:
            status, failure = check(context, deadline)
            if failure is not None:
                return None, failure
            if status == Status.UNSAT:
                return (best, None) if best is not None else (None, ("unsat", ""))
            model = Model.from_context(context, 1)
            try:
                best = number(model, objective)
            finally:
                model.dispose()
            if isinstance(best, bool):
                return None, ("error", "Objective is not an integer term")
            bound = Terms.integer(best)
            context.assert_formula(Terms.arith_lt_atom(objective, bound) if direction == "minimize"
                                   else Terms.arith_gt_atom(objective, bound))
    finally:
        context.dispose()


def blocking(leaves, values):
    """Forbid this exact assignment of the declared outputs."""
    literals = []
    for leaf, value in zip(leaves, values):
        if Terms.is_bool(leaf):
            literals.append(Terms.ynot(leaf) if value else leaf)
        else:
            literals.append(Terms.arith_neq_atom(leaf, Terms.integer(value)))
    # With only constant outputs there is a single possible assignment.
    return Terms.yor(literals) if literals else Terms.false()


def solve(request):
    deadline = time.monotonic() + request["execution_timeout"]
    formulas, logic, outputs, objective = load(request["instance"])
    leaves = list(dict.fromkeys(leaf for leaf in flatten(outputs) if not is_constant(leaf)))

    if objective is not None:
        best, failure = optimum(formulas, logic, objective[0], objective[1], deadline)
        if failure is not None:
            return finish(failure[0], failure[1])
        # Enumerate only assignments achieving the proven optimum, in a fresh context.
        formulas = formulas + [Terms.arith_eq_atom(objective[1], Terms.integer(best))]

    context = fresh(formulas, logic)
    seen = set()
    count = 0
    try:
        while count < request["solution_limit"]:
            status, failure = check(context, deadline)
            if failure is not None:
                return finish(failure[0], failure[1])
            if status == Status.UNSAT:
                return finish("complete" if count else "unsat")
            model = Model.from_context(context, 1)
            try:
                values = [number(model, leaf) for leaf in leaves]
                solution = mapped(outputs, lambda leaf: read(leaf, model))
            finally:
                model.dispose()
            key = tuple(values)
            if key not in seen:
                seen.add(key)
                emit({"type": "solution", "values": solution})
                count += 1
                if count == request["solution_limit"]:
                    break
            context.assert_formula(blocking(leaves, values))
    finally:
        context.dispose()
    finish("limit")


def main():
    try:
        request = json.loads((INPUT / "request.json").read_text())
        if request.get("legacy"):
            return finish("unsupported", "Legacy submissions are not supported by yices_python")

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
        finish("error", f"{type(error).__name__}: {error}" if not isinstance(error, (ValueError, YicesException))
               else str(error))


if __name__ == "__main__":
    main()
