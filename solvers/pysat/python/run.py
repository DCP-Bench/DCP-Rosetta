"""Runner protocol for the pysat integration. Runs inside the image only.

A submission defines `create_model(instance)` (`build` in models retained earlier)
returning `(formula, outputs)`, or `(formula, outputs, objective)` for an optimisation,
where `outputs` maps each declared output name to a literal, a
`pysat.integer.Integer`, a `pysat.integer.LinearExpr` over Integers, a plain
bool, or nested lists of those, and `formula` is one of:

- a `pysat.formula.CNF` for a satisfaction problem, solved with Glucose 4.2;
- a `pysat.formula.WCNF` for an optimisation problem, solved with RC2, the
  MaxSAT solver PySAT ships in `pysat.examples.rc2`, in its stratified form.
  The hard clauses are the constraints and the soft clauses are the
  objective: RC2 minimises the total weight of the soft clauses an assignment
  falsifies. Maximising a quantity means paying for its shortfall. A WCNF
  without soft clauses is a satisfaction problem and goes to Glucose like a
  CNF.

The submission builds the formula with PySAT's own tools: `IDPool` for variable
identifiers, `CardEnc` and `PBEnc` for cardinality and pseudo-Boolean
constraints, `IntegerEngine` plus `Integer` for finite-domain variables, and
`WCNF.append(clause, weight=w)` for soft clauses.

The soft clauses are what RC2 optimises, but their cost is not the problem's
objective: it lacks the objective's constant, and a maximisation pays its
shortfall. So an optimisation also returns `objective`, the problem's own
objective as an expression over the model's variables, in the problem's terms
and direction: an `Integer`, a `LinearExpr` over Integers, or a list of
`(coefficient, term)` pairs whose term is a literal (1 when true, negative
literals included), an
`Integer`, a `LinearExpr` or a bool (a constant: `(c, True)` adds c). The runner
evaluates it on every solution and reports it as the solution's `objective`
(runner protocol 2). It never optimises it: the soft clauses stay the objective
the solver sees. A WCNF with soft clauses but no objective is refused with an
error, since the runner cannot report what the problem's objective is. Two
optima RC2 reports at the same cost must have the same objective value, or the
expression and the soft clauses disagree and the run ends with an error.

Stratified RC2 (`RC2Stratified`) works through the soft clauses heaviest first.
On objectives with many distinct weights, which is what a weighted sum gives,
that is the difference between solving and not: a 15-item knapsack took plain
RC2 over 180 seconds and the stratified form 0.13 seconds. On a single weight
the two coincide.

Optimality is reported only once RC2 has proved it. An RC2 call that is
interrupted at the budget returns no model at all, so a merely good assignment
can never be passed off as an optimal one.

The search runs inside a C extension, so a Python signal handler cannot fire
while it is running. The budget is therefore enforced with PySAT's own
interrupt, driven from a timer thread; the SIGALRM below only covers the pure
Python phase where the submission builds its clauses.

Enumeration blocks the previous **declared outputs**, not the whole assignment:
two models of the same formula routinely agree on everything the problem
declares, and the evaluator counts distinct declared outputs. When optimising,
enumeration stops as soon as the next answer costs more than the optimum.

A `LinearExpr` output is how a value too wide for one `Integer` is declared:
an `Integer` builds one variable per value, so a ten-digit number cannot be one,
but `sum(2**k * bit[k])` over 0..1 Integers can. The runner reads its value off
the assignment and blocks the summed Integers; a different combination that
reaches the same total is skipped rather than reported twice.
"""
import contextlib
import importlib.util
import json
from pathlib import Path
import signal
import sys
import threading
import time

sys.path.insert(0, "/opt/runner")
from runtime import emit  # noqa: E402
from runtime import finish as runtime_finish  # noqa: E402

from pysat.formula import CNF, WCNF  # noqa: E402
from pysat.integer import Integer, LinearExpr  # noqa: E402
from pysat.examples.rc2 import RC2Stratified  # noqa: E402 - loaded here, as start-up, not while the model is built
from pysat.solvers import Solver  # noqa: E402
STARTED = time.monotonic()  # the runner's own clock (benchmarking): read_seconds and main_seconds count from here

# Glucose rather than CaDiCaL: PySAT raises NotImplementedError for
# "limited solve" on CaDiCaL and Lingeling, so those two cannot be stopped
# mid-search and would run until the evaluator killed the container. RC2 uses
# the same Glucose as its SAT oracle, for the same reason.
SOLVER_NAME = "glucose42"

# How far ahead of the hard SIGALRM deadline the solver is interrupted, so the
# runner reports its own timeout rather than losing a race to the signal. RC2
# finishes processing its last core after an interrupt, so it gets more room.
INTERRUPT_MARGIN = 0.5
RC2_INTERRUPT_MARGIN = 2.0

# Seconds from the submission's build until its formula is loaded into Glucose or
# RC2, and from STARTED until the request was read, for benchmarking.
BUILD_SECONDS = 0.0
READ_SECONDS = 0.0


def finish(status, detail="", **metadata):
    runtime_finish(status, detail, build_seconds=BUILD_SECONDS, read_seconds=READ_SECONDS,
                   main_seconds=time.monotonic() - STARTED, **metadata)


class BudgetExceeded(Exception):
    """Raised by the SIGALRM handler, and by nothing a submission can raise."""


def load(instance):
    spec = importlib.util.spec_from_file_location("candidate", "/input/model.py")
    module = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(sys.stderr):
        spec.loader.exec_module(module)
        create_model = getattr(module, "create_model", None) or module.build
        result = create_model(instance)
    if not isinstance(result, tuple) or len(result) not in (2, 3):
        raise ValueError("create_model(instance) must return (formula, outputs), or "
                         "(formula, outputs, objective) for an optimisation")
    formula, outputs = result[:2]
    objective = normalise_objective(result[2]) if len(result) == 3 else None
    if not isinstance(formula, (CNF, WCNF)):
        raise ValueError("the first value must be a pysat.formula.CNF, or a "
                         "pysat.formula.WCNF when the problem has an objective")
    if not isinstance(outputs, dict) or not outputs:
        raise ValueError("create_model(instance) must return a nonempty output dictionary")
    if isinstance(formula, WCNF) and formula.soft and objective is None:
        raise ValueError("an optimisation (a WCNF with soft clauses) must return its objective "
                         "as a third value, (formula, outputs, objective): the problem's own "
                         "objective as an expression over the model's variables, which the "
                         "runner reports on each solution; the soft clauses' cost is not it")
    return formula, outputs, objective


def normalise_objective(objective):
    """The objective as (constant, [(coefficient, term)]), each term a literal,
    an Integer or a LinearExpr. Refuses anything else before the search starts."""
    if isinstance(objective, (Integer, LinearExpr)):
        return 0, [(1, objective)]
    if not isinstance(objective, (list, tuple)):
        raise ValueError("the objective must be an Integer, a LinearExpr over Integers, or a list "
                         f"of (coefficient, term) pairs; got {type(objective).__name__}")
    constant, terms = 0, []
    for pair in objective:
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            raise ValueError("each objective term must be a (coefficient, term) pair; got "
                             f"{pair!r}")
        coefficient, term = pair
        if not isinstance(coefficient, int) or isinstance(coefficient, bool):
            raise ValueError(f"an objective coefficient must be an int; got {coefficient!r}")
        if isinstance(term, bool):
            constant += coefficient * term
        elif isinstance(term, (int, Integer, LinearExpr)):
            terms.append((coefficient, term))
        else:
            raise ValueError("an objective term must be a literal, an Integer, a LinearExpr or "
                             f"a bool; got {type(term).__name__}")
    return constant, terms


def objective_value(objective, model, truth):
    """The problem's objective on this assignment (see normalise_objective)."""
    constant, terms = objective
    total = constant
    for coefficient, term in terms:
        if isinstance(term, Integer):
            total += coefficient * term.decode(model)
        elif isinstance(term, LinearExpr):
            total += coefficient * evaluate(term, model)
        else:
            # A literal counts 1 when true; -v is true when variable v is false.
            total += coefficient * ((term in truth) if term > 0 else (-term not in truth))
    return total


def objective_leaves(objective):
    """The objective's terms, for sizing the dense model."""
    return [] if objective is None else [term for _, term in objective[1]]


def solution(values, objective, model, truth):
    record = {"type": "solution", "values": values}
    if objective is not None:
        record["objective"] = objective_value(objective, model, truth)
    return record


def leaves(node, found):
    if isinstance(node, dict):
        for value in node.values():
            leaves(value, found)
    elif isinstance(node, (list, tuple)):
        for value in node:
            leaves(value, found)
    else:
        found.append(node)
    return found


def render(node, model, truth):
    if isinstance(node, dict):
        return {name: render(value, model, truth) for name, value in node.items()}
    if isinstance(node, (list, tuple)):
        return [render(value, model, truth) for value in node]
    if isinstance(node, Integer):
        return node.decode(model)
    if isinstance(node, LinearExpr):
        return evaluate(node, model)
    if isinstance(node, bool):
        return node
    if isinstance(node, int):
        # A literal from the model's pool, rather than a constant it fixed.
        return node in truth
    raise ValueError("an output leaf must be an Integer, a LinearExpr, a literal, an "
                     f"int or a bool; got {type(node).__name__}")


def evaluate(expression, model):
    """The value of a linear expression over Integers under a model.

    This is how an output too wide for one Integer is declared: as a sum such
    as `sum(2**k * bit[k])` over 0..1 Integers, whose value the runner reads off
    the solver's assignment. Coefficients and the constant must be integers.
    """
    total = expression.const
    for term, coefficient in expression.terms.items():
        if not isinstance(term, Integer):
            raise ValueError("a LinearExpr output may only sum Integers")
        total += coefficient * term.decode(model)
    if total != int(total):
        raise ValueError("a LinearExpr output must have integer coefficients")
    return int(total)


def dense(model, outputs, objective=None):
    """The model as a list indexed by variable, which `Integer.decode` expects.

    RC2 returns only the variables that occur in the formula, so a variable an
    Integer declares but no clause mentions would shift every later index.
    Missing variables are false, which is what a solver would be free to pick.
    """
    top = max([abs(lit) for lit in model] + [0])
    for leaf in leaves(outputs, []) + objective_leaves(objective):
        if isinstance(leaf, Integer):
            top = max(top, leaf.vpool.top)
        elif isinstance(leaf, LinearExpr):
            top = max([top] + [term.vpool.top for term in leaf.terms])
        elif isinstance(leaf, int) and not isinstance(leaf, bool):
            top = max(top, abs(leaf))
    values = [-var for var in range(1, top + 1)]
    for lit in model:
        values[abs(lit) - 1] = lit
    return values


def blocking_clause(outputs, model, truth):
    """Rule out exactly this assignment to the declared outputs."""
    clause = []
    for leaf in leaves(outputs, []):
        if isinstance(leaf, Integer):
            # `equals(v)` is the literal for "this variable takes v", so
            # forbidding the value it took is enough to change the answer.
            clause.append(-leaf.equals(leaf.decode(model)))
        elif isinstance(leaf, LinearExpr):
            # Forbid this combination of the summed Integers. Another
            # combination can reach the same total; the enumeration loop skips
            # such a repeat instead of emitting it twice.
            clause.extend(-term.equals(term.decode(model)) for term in leaf.terms)
        elif isinstance(leaf, bool):
            continue
        elif isinstance(leaf, int):
            clause.append(-leaf if leaf in truth else leaf)
    return clause


def satisfy(formula, outputs, objective, request, started):
    """Enumerate solutions of a satisfaction problem with Glucose."""
    global BUILD_SECONDS
    if isinstance(formula, WCNF):
        formula = CNF(from_clauses=formula.hard)
    limit = request["solution_limit"]
    emitted = 0
    # Declared outputs already reported; see blocking_clause on LinearExpr.
    seen = set()
    with Solver(name=SOLVER_NAME, bootstrap_with=formula) as solver:
        BUILD_SECONDS = time.monotonic() - started
        while emitted < limit:
            left = request["execution_timeout"] - (time.monotonic() - started)
            if left <= 0:
                return finish("timeout", solve_seconds=time.monotonic() - started)
            # The search runs inside a C extension, so the SIGALRM cannot fire
            # until it returns. PySAT's own interrupt is what actually stops
            # it. It is pulled forward by a margin so it always lands before
            # the SIGALRM: armed for the same instant, the two race, and a
            # SIGALRM that wins surfaces as `execution_error` rather than the
            # `timeout` the runner is supposed to report for itself.
            alarm = threading.Timer(max(left - INTERRUPT_MARGIN, 0.01), solver.interrupt)
            alarm.start()
            try:
                answer = solver.solve_limited(expect_interrupt=True)
            finally:
                alarm.cancel()
                solver.clear_interrupt()
            if answer is None:
                return finish("timeout", solve_seconds=time.monotonic() - started)
            if not answer:
                spent = time.monotonic() - started
                return finish("complete" if emitted else "unsat", solve_seconds=spent)
            model = dense(solver.get_model(), outputs, objective)
            truth = {lit for lit in model if lit > 0}
            values = render(outputs, model, truth)
            key = json.dumps(values, sort_keys=True)
            if key not in seen:
                seen.add(key)
                emit(solution(values, objective, model, truth))
                emitted += 1
                if emitted >= limit:
                    break
            clause = blocking_clause(outputs, model, truth)
            if not clause:
                # Nothing the problem declares can differ, so there is no second
                # answer to look for.
                return finish("complete", solve_seconds=time.monotonic() - started)
            solver.add_clause(clause)
    finish("limit", solve_seconds=time.monotonic() - started)


def optimise(formula, outputs, objective, request, started):
    """Enumerate optimal solutions of a weighted formula with RC2."""
    global BUILD_SECONDS
    limit = request["solution_limit"]
    best = None
    # The objective value of the first optimum: every later one, at the same cost,
    # must have it too, or the objective expression and the soft clauses disagree.
    best_value = None
    emitted = 0
    # Declared outputs already reported; see blocking_clause on LinearExpr.
    seen = set()
    with RC2Stratified(formula, solver=SOLVER_NAME) as rc2:
        BUILD_SECONDS = time.monotonic() - started
        while emitted < limit:
            left = request["execution_timeout"] - (time.monotonic() - started)
            if left <= 0:
                return finish("timeout", "the optimum was not proven",
                              solve_seconds=time.monotonic() - started)
            alarm = threading.Timer(max(left - RC2_INTERRUPT_MARGIN, 0.01), rc2.interrupt)
            alarm.start()
            try:
                found = rc2.compute(expect_interrupt=True)
            finally:
                alarm.cancel()
                rc2.clear_interrupt()
            spent = time.monotonic() - started
            if found is None:
                if rc2.interrupted:
                    # RC2 returns no model when interrupted, so there is
                    # nothing proven to report.
                    return finish("timeout", "the optimum was not proven", solve_seconds=spent)
                return finish("complete" if emitted else "unsat", solve_seconds=spent)
            # A model is returned only once every soft-clause assumption is
            # satisfiable, which is RC2's proof of optimality; a timer that
            # fires after that point does not undo it.
            if best is None:
                best = rc2.cost
            elif rc2.cost > best:
                # Every remaining answer is worse, so the optimal ones are done.
                return finish("complete", solve_seconds=spent)
            model = dense(found, outputs, objective)
            truth = {lit for lit in model if lit > 0}
            record = solution(render(outputs, model, truth), objective, model, truth)
            if best_value is None:
                best_value = record["objective"]
            elif record["objective"] != best_value:
                return finish("error", "the objective expression disagrees with the soft clauses: "
                              f"two optima of cost {best} have objective values {best_value} and "
                              f"{record['objective']}", solve_seconds=spent)
            key = json.dumps(record["values"], sort_keys=True)
            if key not in seen:
                seen.add(key)
                emit(record)
                emitted += 1
                if emitted >= limit:
                    break
            clause = blocking_clause(outputs, model, truth)
            if not clause:
                return finish("complete", solve_seconds=time.monotonic() - started)
            rc2.add_clause(clause)
    finish("limit", solve_seconds=time.monotonic() - started)


def main():
    global READ_SECONDS
    request = json.loads(Path("/input/request.json").read_text())
    READ_SECONDS = time.monotonic() - STARTED
    if request.get("legacy"):
        return finish("unsupported", "This integration has no legacy submission format")

    def expired(signum, frame):
        raise BudgetExceeded("Runner execution budget exceeded")

    signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, request["execution_timeout"])

    started = time.monotonic()
    formula, outputs, objective = load(request["instance"])
    if isinstance(formula, WCNF) and formula.soft:
        return optimise(formula, outputs, objective, request, started)
    return satisfy(formula, outputs, objective, request, started)


if __name__ == "__main__":
    try:
        main()
    except BudgetExceeded as error:
        # The SIGALRM fired in Python code, either while the submission was
        # still building its clauses or in the instant after the solver was
        # interrupted. Either way the budget ran out, which is a timeout.
        finish("timeout", str(error))
    except Exception as error:
        import traceback
        traceback.print_exc(file=sys.stderr)
        finish("error", str(error))
