"""Runner protocol for the hexaly_python integration. Runs inside the image only.

A submission defines `build(instance)` returning `(optimizer, outputs)`, where
`optimizer` is the `hexaly.optimizer.HexalyOptimizer` whose model it built. The
model's objectives say whether this is an optimization: none, or one constant
objective, is a satisfaction problem; one other objective gives the direction.

Five things about Hexaly shape this runner.

Hexaly refuses to close a model without an objective, so a satisfaction model
gets `minimize(0)`, which Hexaly reports OPTIMAL as soon as it has a solution.

OPTIMAL means the objective reached its bound within `gap_limit`, 1e-4 relative
by default: on a 40-item knapsack it reported OPTIMAL with the bound 1203 above
the objective. The runner sets the gap limit to 0, so OPTIMAL means proven, and
FEASIBLE at the time limit is an unproven optimum, reported as a timeout.

INFEASIBLE means only that no solution was found; INCONSISTENT is the proof that
none exists. Only INCONSISTENT becomes `unsat`.

Hexaly computes its bounds in threads beside its local search. With one or two
threads the 6x6 job shop ft06 stayed unproven for 30 s; with four it was proven
in 0.4 s, on one CPU. The runner sets four threads; the container's CPU quota
still bounds the time they share.

Hexaly has no enumeration, and after hard no-goods the last solve ends
INFEASIBLE at the time limit, which proves nothing. The runner uses soft
no-goods instead: the objective becomes the number of reported solutions the
declared outputs repeat. Objective 0 is a new solution; a proven minimum of 1 or
more proves that the outputs can take no other value. For an optimization the
objective expression is first pinned to its proven optimum.

Hexaly's log writer is the `sys.stdout` of the moment the optimizer is created,
inside the submission, so the protocol stream keeps file descriptor 1 to itself,
fd 1 goes to stderr, and verbosity is 0.
"""
import contextlib
import importlib.util
import json
import numbers
import os
from pathlib import Path
import signal
import sys
import time

sys.path.insert(0, "/opt/runner")
from runtime import emit, finish  # noqa: E402

import hexaly.optimizer as hx  # noqa: E402

INPUT = Path("/input")
S = hx.HxSolutionStatus
THREADS = 4


def protocol_stream():
    """Give the JSONL protocol its own copy of fd 1 and send fd 1 to stderr."""
    protocol = os.dup(1)
    os.dup2(2, 1)
    sys.stdout = os.fdopen(protocol, "w", buffering=1)


def leaves(value):
    """Every declared output leaf, with Hexaly expressions left whole."""
    if isinstance(value, (list, tuple)):
        return [x for v in value for x in leaves(v)]
    return [value]


def kind(expression):
    """How a declared output expression is read: a scalar, a list decision or an array.

    Hexaly types an expression when the model is closed and answers only then.
    """
    if expression.is_bool() or expression.is_int():
        return "scalar"
    if expression.is_double():
        raise ValueError("A declared output is a float expression (from /, ** or a float decision); "
                         "outputs must be integers: use //, x * x or integer decisions")
    if expression.is_collection():
        if expression.operator == hx.HxOperator.LIST:
            return "list"
        raise ValueError("A declared output is a set; sets have no order, so declare "
                         "model.contains(s, i) for each i, or use a list decision")
    if expression.is_array():
        return "array"
    if expression.is_interval():
        raise ValueError("A declared output is an interval; declare model.start(t) or model.end(t)")
    raise ValueError(f"Unsupported declared output expression (operator {expression.operator})")


def integer(value):
    """One leaf value from Hexaly: an int, never a float."""
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, numbers.Integral):
        return int(value)
    raise ValueError(f"Declared outputs must be integer valued; got {value!r}")


def array_value(value):
    return [array_value(v) if isinstance(v, hx.HxArray) else integer(v) for v in value]


def read(leaf):
    """The value of one declared output leaf in the current solution."""
    if isinstance(leaf, bool):
        return leaf
    if isinstance(leaf, numbers.Integral):
        return int(leaf)
    if not isinstance(leaf, hx.HxExpression):
        raise ValueError("Declared outputs must be integers, Booleans or Hexaly expressions; "
                         f"got {type(leaf).__name__}")
    shape = kind(leaf)
    if leaf.is_undefined():
        raise ValueError("A declared output is undefined in the solution (an at() out of range, "
                         "or a value of an absent interval)")
    if shape == "scalar":
        return integer(leaf.value)
    if shape == "list":
        return [integer(v) for v in leaf.value]
    return array_value(leaf.value)


def resolved(value):
    """The declared outputs with every leaf replaced by its value."""
    if isinstance(value, dict):
        return {k: resolved(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [resolved(v) for v in value]
    return read(value)


def matches(model, leaf, shape, value):
    """Boolean expressions that all hold exactly when the leaf takes this value again.

    Built while the model is open, when Hexaly cannot type expressions, so the shape
    comes from kind() on the closed model and nested arrays follow the value.
    """
    if shape == "scalar":
        return [leaf == value]
    if shape == "list":
        # index() is -1 for an absent element, where at() would make the solution infeasible.
        return [model.count(leaf) == len(value)] + [model.index(leaf, v) == i for i, v in enumerate(value)]
    terms = []
    for i, v in enumerate(value):
        element = model.at(leaf, i)
        terms += matches(model, element, "array", v) if isinstance(v, list) else [element == v]
    return terms


def load(instance):
    spec = importlib.util.spec_from_file_location("candidate", str(INPUT / "model.py"))
    module = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(sys.stderr):
        spec.loader.exec_module(module)
        returned = module.build(instance)
    if not isinstance(returned, tuple) or len(returned) != 2:
        raise ValueError("build(instance) must return (optimizer, outputs)")
    optimizer, outputs = returned
    if not isinstance(optimizer, hx.HexalyOptimizer):
        raise ValueError("build(instance) must return the hexaly.optimizer.HexalyOptimizer it built "
                         f"the model in, not {type(optimizer).__name__}")
    if not isinstance(outputs, dict) or not outputs:
        raise ValueError("build(instance) must return a nonempty output dictionary")
    return optimizer, outputs


def configure(optimizer):
    """The settings that decide what a verdict means; they override the submission's."""
    param = optimizer.param
    param.verbosity = 0
    param.nb_threads = THREADS
    param.set_gap_limit(0)


def objective_of(model):
    """The single objective expression, or None for a satisfaction problem.

    Called on the closed model, the only state in which Hexaly types expressions.
    """
    count = model.nb_objectives
    if count > 1:
        raise NotImplementedError("Only a single objective is supported; Hexaly would optimise "
                                  f"{count} objectives lexicographically")
    objective = model.get_objective(0)
    if objective.is_constant():
        return None
    if objective.is_double():
        raise ValueError("The objective is a float expression (from /, ** or a float decision); "
                         "declare an integer objective")
    return objective


def attempt(optimizer, deadline):
    """Solve once within the whole seconds left; None when no full second is left."""
    left = int(deadline - time.monotonic())
    if left < 1:
        return None
    optimizer.param.time_limit = left
    with contextlib.redirect_stdout(sys.stderr):
        optimizer.solve()
    return optimizer.solution.status


def solve(request):
    deadline = time.monotonic() + request["execution_timeout"]
    optimizer, outputs = load(request["instance"])
    model = optimizer.model
    with contextlib.redirect_stdout(sys.stderr):
        configure(optimizer)
        if not model.is_closed():
            if model.nb_objectives == 0:
                model.minimize(0)
            model.close()
        objective = objective_of(model)

    status = attempt(optimizer, deadline)
    if status is None:
        return finish("timeout")
    if status == S.INCONSISTENT:
        return finish("unsat")
    if status == S.FEASIBLE and objective is not None:
        return finish("timeout", "Candidate optimum was not proven")
    if status != S.OPTIMAL:
        return finish("timeout", f"No proven result within the time limit (Hexaly status {status.name})")

    # The proven optimum: Hexaly's value of the model's own objective expression, constant and direction included.
    # Every solution after the first is pinned to it.
    optimum = None if objective is None else integer(objective.value)
    limit = request["solution_limit"]
    seen, repeats = set(), []
    while True:
        values = resolved(outputs)
        key = json.dumps(values, sort_keys=True)
        if key in seen:
            return finish("error", "Hexaly returned a solution already reported; the declared outputs "
                                   "could not be excluded")
        seen.add(key)
        emit({"type": "solution", "values": values, **({} if optimum is None else {"objective": optimum})})
        if len(seen) >= limit:
            return finish("limit")

        found = [(leaf, kind(leaf), read(leaf)) for leaf in leaves(list(outputs.values()))
                 if isinstance(leaf, hx.HxExpression)]
        best = None if objective is None else objective.value
        with contextlib.redirect_stdout(sys.stderr):
            model.open()
            terms = [t for leaf, shape, value in found for t in matches(model, leaf, shape, value)]
            if not terms:
                # Every declared output is a constant: no other value exists.
                return finish("complete")
            model.remove_objective(0)
            if objective is not None:
                # Only assignments that achieve the proven optimum may be enumerated.
                model.constraint(objective == best)
                objective = None
            repeats.append(model.and_(*terms))
            model.minimize(model.sum(repeats))
            model.close()

        status = attempt(optimizer, deadline)
        if status is None:
            return finish("timeout")
        if status == S.INCONSISTENT:
            return finish("complete")
        if status not in (S.OPTIMAL, S.FEASIBLE):
            return finish("timeout")
        if model.get_objective(0).value >= 1:
            # Every assignment found repeats a reported one; only a proven minimum says none is left.
            return finish("complete") if status == S.OPTIMAL else finish("timeout")


def main():
    protocol_stream()
    try:
        request = json.loads((INPUT / "request.json").read_text())
        if request.get("legacy"):
            return finish("unsupported", "Legacy submissions are not supported by hexaly_python")

        def expired(signum, frame):
            raise TimeoutError("Runner execution budget exceeded")

        signal.signal(signal.SIGALRM, expired)
        signal.setitimer(signal.ITIMER_REAL, request["execution_timeout"] + 5)
        solve(request)
    except TimeoutError:
        finish("timeout")
    except hx.HxError as error:
        import traceback
        traceback.print_exc(file=sys.stderr)
        finish("error", f"Hexaly error: {error}")
    except NotImplementedError as error:
        finish("unsupported", str(error))
    except Exception as error:
        import traceback
        traceback.print_exc(file=sys.stderr)
        finish("error", f"{type(error).__name__}: {error}")


if __name__ == "__main__":
    main()
