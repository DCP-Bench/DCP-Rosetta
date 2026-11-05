"""Runner protocol for the hermax integration. Runs inside the image only.

A submission defines `create_model(instance)` returning `(model, outputs)`, or
`(model, outputs, objective)` for an optimisation, where `model` is a
`hermax.model.Model` and `outputs` maps each declared output name to variables
of that model. Models retained before the rename define `build(instance)`,
which is still accepted. The file is loaded as module "candidate", so its
`if __name__ == "__main__":` run block never runs here.

**The objective the solver optimises goes on the model.** A MaxSAT solver
minimises the weight of the soft clauses it breaks, so an objective is written
the way hermax writes one -- `model.obj += expr`, which hermax turns into
weighted soft clauses (the `model.obj[weight] += literal` form of 1.2 raises
TypeError since 1.3.0). Maximising a quantity means paying for its complement.
The runner knows an objective exists from `result.cost`: hermax leaves that
None for a model with no soft clauses.

**The objective the runner reports is returned.** The cost is the problem's
objective only for a minimisation given to `model.obj` as is; a maximisation
pays its complement. So an optimisation also returns `objective`, the problem's
own objective in its own terms and direction, as anything `result[...]` decodes
to a number (an IntVar, a Literal, a linear expression, an int). The runner
reports its value on each solution as `objective` (runner protocol 2). An
optimisation without it is refused with an error before anything is emitted,
and two optima of the same cost with different objective values (the
expression and the soft clauses disagree) end the run with an error.

Routing an objective through an auxiliary integer variable instead, with
`sum(...) == total`, was a trap in hermax 1.2 (43 seconds to encode that one
equality on a four-by-four assignment); in 1.3.0 it works but is still slower
than giving the sum to `model.obj` directly.

Optimality is reported only on the `optimum` status. `interrupted_sat` means a
solution was found without proving it best, which is a timeout here rather than
an answer, because the evaluator would otherwise compare it against the
reference optimum as if it were one.

An output may also be a linear expression of the model's variables, which is
how a value too wide for one `IntVar` is declared: hermax encodes an IntVar
with one literal per value, so an IntVar over a ten-digit range exhausts memory
by itself, while `sum(10**(9-i) * digit[i])` over 0..9 IntVars or
`sum(2**k * bit[k])` over Booleans does not. Such a sum is hermax's own
`PBExpr` (a single weighted literal is a `Term`), which `result[...]` decodes
since 1.2.9; when enumerating, the runner blocks the literals and variables
the expression sums. Another combination of
those can reach the same total, so a declared output equal to one already
reported is skipped rather than emitted twice.
"""
import contextlib
import functools
import importlib.util
import json
import operator
from pathlib import Path
import sys
import time

sys.path.insert(0, "/opt/runner")
from runtime import emit, mapped  # noqa: E402
from runtime import finish as runtime_finish  # noqa: E402

from hermax.model import (BoolMatrix, IntMatrix, IntVar, Literal, Model,  # noqa: E402
                          PBExpr, Term)
STARTED = time.monotonic()  # the runner's own clock (benchmarking): read_seconds and main_seconds count from here

# `ok` on a SolveResult also covers interrupted_sat, which is not an answer here;
# `proven` is true only for sat, optimum and unsat.
ANSWERED = ("sat", "optimum")

# Seconds the submission took to build its model, and from STARTED until the request
# was read, for benchmarking. hermax hands the model to its solver only inside
# solve(), so that hand-off counts as search.
BUILD_SECONDS = 0.0
READ_SECONDS = 0.0


def finish(status, detail="", **metadata):
    runtime_finish(status, detail, build_seconds=BUILD_SECONDS, read_seconds=READ_SECONDS,
                   main_seconds=time.monotonic() - STARTED, **metadata)


def load(instance):
    """Import the submission and normalise what it returned."""
    spec = importlib.util.spec_from_file_location("candidate", "/input/model.py")
    module = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(sys.stderr):
        spec.loader.exec_module(module)
        create_model = getattr(module, "create_model", None) or module.build
        returned = create_model(instance)
    if not isinstance(returned, tuple) or len(returned) not in (2, 3):
        raise ValueError("create_model(instance) must return (model, outputs), or "
                         "(model, outputs, objective) for an optimisation, with the objective "
                         "the solver minimises declared on model.obj")
    model, outputs = returned[:2]
    objective = returned[2] if len(returned) == 3 else None
    if not isinstance(model, Model):
        raise ValueError("the first value must be a hermax.model.Model")
    if not isinstance(outputs, dict) or not outputs:
        raise ValueError("create_model(instance) must return a nonempty output dictionary")
    if len(returned) == 3 and not (isinstance(objective, (int, IntVar, Literal, PBExpr, Term))
                                   or type(objective).__module__.startswith("hermax.")):
        raise ValueError("the objective must be an IntVar, a Literal, a linear expression of "
                         f"them or an int; got {type(objective).__name__}")
    return model, outputs, objective


# Reported when an optimisation returned no objective.
MISSING_OBJECTIVE = ("an optimisation (a model with soft clauses on model.obj) must return its "
                     "objective as a third value, (model, outputs, objective): the problem's own "
                     "objective as an expression of the model's variables, which the runner "
                     "reports on each solution; the solver's cost is not it")


def objective_value(objective, result):
    """The problem's objective on this solution, as an int."""
    value = objective if isinstance(objective, int) else result[objective]
    if isinstance(value, bool) or (isinstance(value, float) and value.is_integer()):
        value = int(value)
    if not isinstance(value, int):
        raise ValueError(f"the objective decoded to {value!r}, not an integer")
    return value


def atoms(node, found):
    """Every individual variable under the declared outputs, for blocking."""
    if isinstance(node, dict):
        for value in node.values():
            atoms(value, found)
    elif isinstance(node, (BoolMatrix, IntMatrix)):
        atoms(list(node.flatten()), found)
    elif isinstance(node, (list, tuple)) or hasattr(node, "__iter__"):
        for value in node:
            atoms(value, found)
    else:
        found.append(node)
    return found


def summed(expression):
    """The weighted literals and derived integers a PBExpr or Term adds up."""
    if isinstance(expression, Term):
        return [(expression.coefficient, expression.literal)], 0
    return ([(term.coefficient, term.literal) for term in expression.terms]
            + list(expression.int_terms), expression.constant)


def blocking_clause(outputs, result):
    """Rule out exactly this assignment to the declared outputs.

    For an expression output, that means this assignment to every literal and
    variable it sums, not this total: a total cannot be forbidden by a clause.
    """
    disjuncts = []
    for leaf in atoms(outputs, []):
        if isinstance(leaf, (PBExpr, Term)):
            items = [item for _, item in summed(leaf)[0]]
        elif isinstance(leaf, (IntVar, Literal)):
            items = [leaf]
        else:
            raise ValueError("an output leaf must be an IntVar, a Literal, or a linear "
                             f"expression of them; got {type(leaf).__name__}")
        for item in items:
            value = result[item]
            if isinstance(item, Literal):
                disjuncts.append(~item if value else item)
                continue
            different = item != value
            if not isinstance(different, Literal):
                # A derived integer such as x // 3 compares to a PB constraint,
                # which hermax cannot put in a clause.
                raise ValueError("an output expression can only be enumerated over "
                                 "literals and integer variables; got "
                                 f"{type(item).__name__}")
            disjuncts.append(different)
    if not disjuncts:
        return None
    return functools.reduce(operator.or_, disjuncts)


def main():
    global BUILD_SECONDS, READ_SECONDS
    request = json.loads(Path("/input/request.json").read_text())
    READ_SECONDS = time.monotonic() - STARTED
    if request.get("legacy"):
        return finish("unsupported", "This integration has no legacy submission format")

    started = time.monotonic()
    deadline = started + request["execution_timeout"]
    model, outputs, objective = load(request["instance"])
    BUILD_SECONDS = time.monotonic() - started

    limit = request["solution_limit"]
    best = None
    # The objective value of the first optimum: every later one, at the same cost,
    # must have it too, or the objective expression and the soft clauses disagree.
    best_value = None
    emitted = 0
    # Declared outputs already reported; see blocking_clause on expressions.
    seen = set()
    while emitted < limit:
        left = deadline - time.monotonic()
        if left <= 0:
            return finish("timeout", "the budget ran out before the search finished",
                          solve_seconds=time.monotonic() - started)
        result = model.solve(time_limit=left)
        spent = time.monotonic() - started
        status = result.status
        if status == "error":
            return finish("error", "the MaxSAT solver reported an error", solve_seconds=spent)
        if not result.proven:
            detail = ("the optimum was not proven" if result.cost is not None
                      else "the search did not finish")
            return finish("timeout", detail, solve_seconds=spent)
        if status == "unsat":
            return finish("complete" if emitted else "unsat", solve_seconds=spent)
        if status not in ANSWERED:
            return finish("error", f"unexpected solver status {status}", solve_seconds=spent)
        # hermax leaves cost None when the model declares no soft clauses.
        if result.cost is not None:
            if objective is None:
                return finish("error", MISSING_OBJECTIVE, solve_seconds=spent)
            if best is None:
                best = result.cost
            elif result.cost > best:
                # Every remaining answer is worse, so the optimal ones are done.
                return finish("complete", solve_seconds=spent)

        record = {"type": "solution", "values": mapped(outputs, lambda leaf: result[leaf])}
        if objective is not None:
            record["objective"] = objective_value(objective, result)
            if result.cost is not None:
                if best_value is None:
                    best_value = record["objective"]
                elif record["objective"] != best_value:
                    return finish("error", "the objective expression disagrees with the soft "
                                  f"clauses: two optima of cost {best} have objective values "
                                  f"{best_value} and {record['objective']}", solve_seconds=spent)
        key = json.dumps(record["values"], sort_keys=True)
        if key not in seen:
            seen.add(key)
            emit(record)
            emitted += 1
            if emitted >= limit:
                break
        clause = blocking_clause(outputs, result)
        if clause is None:
            return finish("complete", solve_seconds=time.monotonic() - started)
        model &= clause
    finish("limit", solve_seconds=time.monotonic() - started)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        import traceback
        traceback.print_exc(file=sys.stderr)
        finish("error", str(error))
