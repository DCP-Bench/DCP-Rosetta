"""Runner protocol for the Paramita (Python) integration. Runs inside the image only.

A submission is written against `paramita` and defines `create_model(instance)`
(`build` in models retained earlier), which returns `(formula, pool), outputs`
for a satisfaction problem and `(formula, pool), outputs, objective` for an
optimisation:

- `formula` is a `paramita.containers.CnfFormula` for a satisfaction problem, or
  a `WcnfFormula` for an optimisation problem: its hard clauses are the
  constraints and its soft clauses the objective. MaxSAT maximises the satisfied
  soft weight, so a model that minimises encodes the negated objective. A
  WcnfFormula without soft clauses is a satisfaction problem.
- `pool` is the `paramita.modelling.DimacsVariablePool` the model encoded with.
  It gives each Bool its variable number, and the runner decodes with it.
- `outputs` maps each declared name to one of: a Bool or a Boolean expression
  over Bools, read as a JSON boolean; an integer expression over Bools, read as
  a JSON integer; an int or bool constant; or nested lists and dicts of these.
  Each is read with `paramita.modelling.evaluate` over the solver's assignment.
  An output Bool the formula never mentions is unconstrained: the runner blocks
  over it like any other, and reads it false until the solver has seen it.
- `objective` is the problem's own objective, in its own terms and direction: an
  integer expression over Bools (or a Bool, or an int). The soft clauses are
  what EvalMaxSAT optimises, and its benefit is not the problem's value (a
  minimisation encodes the negation; the encoding may shift it by a constant),
  so the runner evaluates this expression on each optimum and reports it as the
  solution's `objective` (runner protocol 2). A WcnfFormula with soft clauses
  returned without it is refused with an error, and two optima of the same
  benefit with different objective values (the expression and the soft clauses
  disagree) end the run with an error.

The runner encodes nothing itself. It copies the clauses into a solver:

- satisfaction: `SatSolver.from_name("Cadical300")`, `add_clauses`;
- optimisation: `MaxSatSolver.from_name("EvalMaxSAT2022")`, the hard clauses,
  then `add_clause(clause, weight)` per soft clause (a zero weight included).

Integer outputs are read in Python integers, so an output such as a ten-digit
number is exact; paramita's own `evaluate` computes in 32 bits and wraps.

Satisfaction enumerates up to the solution limit, blocking the declared output
Bools rather than the whole assignment, so two models that agree on every
output count once. CaDiCaL supports only a conflict budget, so its search runs
in conflict-limited calls, and the clock is checked between them.

Optimisation reports only proven optima. EvalMaxSAT has no budget and ignores
interrupts, so it runs in a forked child that the parent kills at the deadline
or the solution limit. The child solves, sends the output Bools of an optimum,
blocks them with a hard clause and solves again, until the answer is no longer
optimal or its benefit falls below the first optimum's. The parent renders,
deduplicates and emits each optimum as it arrives.

Standard output is the protocol channel. EvalMaxSAT writes stray `c ...` lines
to file descriptor 1, so before any plugin loads, descriptor 1 is pointed at
descriptor 2 and the protocol is written to a saved copy of the original.

The default PB encoder, which models call, recurses once per term, so a PB
constraint over about a thousand Bools overflows the default 8 MB stack and the
process dies with signal 11. The runner therefore raises its stack limit to the
hard limit and re-executes itself before doing anything else. Run inside another
program's process (a benchmark harness, through runpy), it cannot re-execute
without taking that program with it, so it raises the limit in place: the main
thread's stack then grows to the new limit, as far as the memory map leaves room.
"""
import os
import resource
import sys

_SOFT, _HARD = resource.getrlimit(resource.RLIMIT_STACK)
if _SOFT != _HARD and os.environ.get("DCP_STACK_RAISED") != "1":
    resource.setrlimit(resource.RLIMIT_STACK, (_HARD, _HARD))
    # runpy sets sys.argv[0] to this file too; only the interpreter's own command
    # line tells whether this runner is the program.
    if os.path.realpath(__file__) in map(os.path.realpath, sys.orig_argv[1:]):
        os.environ["DCP_STACK_RAISED"] = "1"
        os.execv(sys.executable, [sys.executable] + sys.argv)
# `sum(...)` over n Bools is a chain of n nested additions, and the expression
# walkers below and in paramita recurse once per link: a flat sum of about a
# thousand terms exceeds Python's default depth of 1000. The raised stack holds
# the deeper recursion.
sys.setrecursionlimit(1_000_000)

# Taken before any paramita import, because the plugins print to descriptor 1
# when they load and when EvalMaxSAT reports a hard-clause conflict.
_STDOUT = sys.stdout
_PROTOCOL = os.fdopen(os.dup(1), "w", buffering=1)
os.dup2(2, 1)
sys.stdout = _PROTOCOL

import contextlib  # noqa: E402
import importlib.util  # noqa: E402
import json  # noqa: E402
import multiprocessing  # noqa: E402
from pathlib import Path  # noqa: E402
import signal  # noqa: E402
import time  # noqa: E402
import traceback  # noqa: E402

sys.path.insert(0, "/opt/runner")
from runtime import emit  # noqa: E402
from runtime import finish as runtime_finish  # noqa: E402

from paramita.containers import CnfFormula, WcnfFormula  # noqa: E402
from paramita.modelling import (  # noqa: E402
    Bool,
    BinaryIntegerOperation,
    BinaryOperation,
    DimacsVariablePool,
    PseudoBooleanOperation,
    UnaryIntegerOperation,
    UnaryOperation,
    evaluate,
)
from paramita.solvers import MAXSAT_ANSWER, MaxSatSolver, SatSolver, SolvingBudget  # noqa: E402
STARTED = time.monotonic()  # the runner's own clock (benchmarking): read_seconds and main_seconds count from here

SAT_SOLVER = "Cadical300"
MAXSAT_SOLVER = "EvalMaxSAT2022"

# Conflicts per CaDiCaL call. Small enough that the clock is checked often,
# large enough that the calls themselves are not the cost.
CONFLICT_CHUNK = 5000

# Time the runner's own deadline keeps ahead of the SIGALRM, so the runner
# reports its own timeout rather than losing a race to the signal.
SIGNAL_MARGIN = 0.5

# Time kept back from the deadline when waiting on EvalMaxSAT, so the runner
# can still report its own timeout rather than losing a race to SIGALRM.
MAXSAT_MARGIN = 0.5

BOOLEAN_EXPRESSIONS = (Bool, UnaryOperation, BinaryOperation, PseudoBooleanOperation)
INTEGER_EXPRESSIONS = (UnaryIntegerOperation, BinaryIntegerOperation)

# Seconds from the submission's build until its clauses are copied into the
# solver, and from STARTED until the request was read, for benchmarking.
BUILD_SECONDS = 0.0
READ_SECONDS = 0.0


def finish(status, detail="", **metadata):
    runtime_finish(status, detail, build_seconds=BUILD_SECONDS, read_seconds=READ_SECONDS,
                   main_seconds=time.monotonic() - STARTED, **metadata)


class BudgetExceeded(Exception):
    """Raised by the SIGALRM handler, and by nothing a submission can raise."""


class Deadline:
    """The runner's own budget, ending a little before the SIGALRM that backs it up."""

    def __init__(self, request, started):
        self.limit = request["execution_timeout"] - SIGNAL_MARGIN
        self.started = started

    def left(self):
        return self.limit - (time.monotonic() - self.started)

    def spent(self):
        return time.monotonic() - self.started


FORM = "create_model(instance) must return (formula, pool), outputs"


def load(instance):
    spec = importlib.util.spec_from_file_location("candidate", "/input/model.py")
    module = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(sys.stderr):
        spec.loader.exec_module(module)
        create_model = getattr(module, "create_model", None) or getattr(module, "build", None)
        if create_model is None:
            raise ValueError("the model defines no create_model(instance)")
        result = create_model(instance)
    if not isinstance(result, tuple) or len(result) not in (2, 3):
        raise ValueError(f"{FORM}; got {type(result).__name__}")
    model, outputs = result[:2]
    objective = result[2] if len(result) == 3 else None
    if isinstance(model, (CnfFormula, WcnfFormula)):
        raise ValueError(f"{FORM}; the formula comes with the DimacsVariablePool it was "
                         "encoded with, as the pair (formula, pool)")
    if not isinstance(model, tuple) or len(model) != 2:
        raise ValueError(f"{FORM}; the first value must be the pair (formula, pool), got "
                         f"{type(model).__name__}: constraints are encoded into a CnfFormula or "
                         "WcnfFormula with add_to_container or add_to_weighted_container, "
                         "not returned as expressions")
    formula, pool = model
    if not isinstance(formula, (CnfFormula, WcnfFormula)):
        raise ValueError(f"{FORM}; formula must be a paramita.containers.CnfFormula or "
                         f"WcnfFormula, got {type(formula).__name__}")
    if not isinstance(pool, DimacsVariablePool):
        raise ValueError(f"{FORM}; pool must be the paramita.modelling.DimacsVariablePool the "
                         f"model encoded with, got {type(pool).__name__}")
    if not isinstance(outputs, dict) or not outputs:
        raise ValueError(f"{FORM}; outputs must be a nonempty dictionary")
    if objective is not None:
        if isinstance(objective, (list, tuple, dict)):
            raise ValueError("the objective must be one integer expression over Bools, a Bool "
                             f"or an int; got a {type(objective).__name__}")
        bool_names(objective, set())  # refuses a leaf no expression can be
    elif isinstance(formula, WcnfFormula) and formula.soft_clauses():
        raise ValueError(f"{FORM}, objective; an optimisation (a WcnfFormula with soft clauses) "
                         "must return its objective as a third value: the problem's own objective "
                         "as an integer expression over Bools, which the runner reports on each "
                         "solution; the soft clauses' benefit is not it")
    return formula, pool, outputs, objective


def bool_names(node, found):
    """Every Bool name an output mentions; refuses a leaf no output can be."""
    if isinstance(node, Bool):
        found.add(node.name)
    elif isinstance(node, (list, tuple)):
        for value in node:
            bool_names(value, found)
    elif isinstance(node, dict):
        for value in node.values():
            bool_names(value, found)
    elif isinstance(node, (UnaryOperation, UnaryIntegerOperation)):
        bool_names(node.operand, found)
    elif isinstance(node, (BinaryOperation, BinaryIntegerOperation, PseudoBooleanOperation)):
        bool_names(node.lhs, found)
        bool_names(node.rhs, found)
    elif not isinstance(node, int):  # bool is an int
        raise ValueError("an output leaf must be a Bool, a Boolean or integer expression "
                         f"over Bools, an int or a bool; got {type(node).__name__}")
    return found


def render(node, truth):
    """The declared outputs with their values under `truth`, a name -> bool map."""
    if isinstance(node, dict):
        return {name: render(value, truth) for name, value in node.items()}
    if isinstance(node, (list, tuple)):
        return [render(value, truth) for value in node]
    if isinstance(node, int):  # bool included
        return node
    if isinstance(node, INTEGER_EXPRESSIONS):
        return exact_value(node, truth)
    value = evaluate(node, truth)
    if isinstance(value, int):
        return value
    raise ValueError(f"an output evaluated to {type(value).__name__}")


def exact_value(node, truth):
    """An integer expression's value in Python integers. paramita's `evaluate`
    computes in 32 bits and wraps; an output such as a ten-digit number must not."""
    if isinstance(node, int):
        return int(node)
    if isinstance(node, UnaryIntegerOperation):
        return -exact_value(node.operand, truth)
    if isinstance(node, BinaryIntegerOperation):
        lhs, rhs = exact_value(node.lhs, truth), exact_value(node.rhs, truth)
        return lhs * rhs if node.operator == BinaryIntegerOperation.Type.MULTIPLY else lhs + rhs
    # A Bool or Boolean expression inside a sum counts as 0 or 1.
    return int(evaluate(node, truth))


def output_variables(pool, outputs, objective=None):
    """(names, variables) of every output Bool, then every further Bool the
    objective names, numbered by the model's pool, and how many of them are
    outputs: only those are blocked.

    Taken before any solver or fork. `get_variable` numbers a Bool the formula
    never mentions with a fresh variable; that Bool is free, and the solver
    learns of it from the first blocking clause."""
    names = sorted(bool_names(outputs, set()))
    extra = [] if objective is None else sorted(bool_names(objective, set()) - set(names))
    return names + extra, [pool.get_variable(name) for name in names + extra], len(names)


def values_of(model, variables):
    """The output Bools' values in a solver model. A variable the solver has not
    seen is unconstrained, so false is a model; it is what the runner reports."""
    truth = {abs(literal): literal > 0 for literal in model}
    return [truth.get(variable, False) for variable in variables]


def blocking_clause(variables, values):
    """Rule out exactly this combination of the output Bools."""
    return [-variable if value else variable for variable, value in zip(variables, values)]


class Emitter:
    """Renders, deduplicates and emits solutions with their objective; counts the
    distinct ones."""

    def __init__(self, outputs, objective, names, limit):
        self.outputs, self.objective, self.names, self.limit = outputs, objective, names, limit
        self.seen = set()
        # (benefit, objective value) of the first optimum, which every later one shares.
        self.first = None

    @property
    def count(self):
        return len(self.seen)

    def full(self):
        return self.count >= self.limit

    def offer(self, values, benefit=None):
        """Emits the solution unless it repeats one; returns an error detail instead
        when its objective disagrees with the first optimum's at the same benefit."""
        truth = dict(zip(self.names, values))
        record = {"type": "solution", "values": render(self.outputs, truth)}
        if self.objective is not None:
            # exact_value reads a Bool as 0/1 and an int as itself.
            record["objective"] = exact_value(self.objective, truth)
            if benefit is not None:
                if self.first is None:
                    self.first = (benefit, record["objective"])
                elif benefit == self.first[0] and record["objective"] != self.first[1]:
                    return ("the objective expression disagrees with the soft clauses: two optima "
                            f"of benefit {benefit} have objective values {self.first[1]} and "
                            f"{record['objective']}")
        key = json.dumps(record["values"], sort_keys=True)
        if key not in self.seen:
            self.seen.add(key)
            emit(record)
        return None


def solve_within(solver, deadline):
    """CaDiCaL in conflict-limited calls, checking the clock between them.

    Returns True, False, or "timeout" once the deadline has passed.
    """
    while True:
        if deadline.left() <= 0:
            return "timeout"
        answer = solver.solve(budget=SolvingBudget(num_conflicts=CONFLICT_CHUNK))
        if answer is not None:
            return answer


def satisfy(clauses, variables, blocked, emitter, deadline):
    global BUILD_SECONDS
    solver = SatSolver.from_name(SAT_SOLVER)
    solver.add_clauses(clauses)
    BUILD_SECONDS = deadline.spent()
    while not emitter.full():
        answer = solve_within(solver, deadline)
        if answer == "timeout":
            return finish("timeout", solve_seconds=deadline.spent())
        if not answer:
            return finish("complete" if emitter.count else "unsat", solve_seconds=deadline.spent())
        values = values_of(solver.model(), variables)
        emitter.offer(values)
        if not blocked:
            # The outputs depend on nothing the solver chooses, so there is no
            # second answer to look for.
            return finish("complete", solve_seconds=deadline.spent())
        solver.add_clause(blocking_clause(variables[:blocked], values[:blocked]))
    return finish("limit", solve_seconds=deadline.spent())


def _optima_worker(solver, variables, blocked, connection):
    """Runs in a forked child: sends ("optimum", values, benefit) per optimum, the
    values of `variables` of which the first `blocked` are blocked, then one of
    ("unsat",), ("worse",), ("done",), ("answer", name) or ("error", detail).
    Only a kill from the parent stops it otherwise."""
    try:
        first = None
        while True:
            answer = solver.solve()
            if answer == MAXSAT_ANSWER.UNSATISFIABLE:
                connection.send(("unsat",))
                return
            if answer != MAXSAT_ANSWER.OPTIMAL:
                connection.send(("answer", answer.name))
                return
            benefit = solver.benefit()
            if first is None:
                first = benefit
            elif benefit < first:
                connection.send(("worse",))
                return
            values = values_of(solver.model(), variables)
            connection.send(("optimum", values, benefit))
            if not blocked:
                connection.send(("done",))
                return
            solver.add_clause(blocking_clause(variables[:blocked], values[:blocked]))
    except Exception as error:  # reported to the parent, which turns it into a status
        connection.send(("error", repr(error)))
    finally:
        connection.close()


def optimise(formula, variables, blocked, emitter, deadline):
    global BUILD_SECONDS
    solver = MaxSatSolver.from_name(MAXSAT_SOLVER)
    solver.add_clauses(formula.hard_clauses())
    for weight, clause in formula.soft_clauses():
        solver.add_clause(clause, weight)
    BUILD_SECONDS = deadline.spent()

    context = multiprocessing.get_context("fork")
    receiver, sender = context.Pipe(duplex=False)
    worker = context.Process(target=_optima_worker, args=(solver, variables, blocked, sender))
    worker.start()
    sender.close()
    try:
        while True:
            wait = deadline.left() - MAXSAT_MARGIN
            if wait <= 0 or not receiver.poll(wait):
                if emitter.count:
                    return finish("timeout", "the optimum was proven, the enumeration was not",
                                  solve_seconds=deadline.spent())
                return finish("timeout", "the optimum was not proven", solve_seconds=deadline.spent())
            try:
                message = receiver.recv()
            except EOFError:
                message = ("error", "the MaxSAT process ended without an answer")
            kind = message[0]
            if kind == "optimum":
                disagreement = emitter.offer(message[1], message[2])
                if disagreement:
                    return finish("error", disagreement, solve_seconds=deadline.spent())
                if emitter.full():
                    return finish("limit", solve_seconds=deadline.spent())
                continue
            if not emitter.count:
                if kind == "unsat":
                    return finish("unsat", solve_seconds=deadline.spent())
                detail = message[1] if len(message) > 1 else kind
                return finish("error", f"MaxSAT failed: {detail}")
            if kind in ("unsat", "worse", "done"):
                return finish("complete", solve_seconds=deadline.spent())
            # The optima found so far stand; the rest of the enumeration is unknown.
            return finish("timeout", f"the optimum was proven, the enumeration was not: {message}",
                          solve_seconds=deadline.spent())
    finally:
        if worker.is_alive():
            worker.kill()
        worker.join()
        receiver.close()


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
    deadline = Deadline(request, started)
    formula, pool, outputs, objective = load(request["instance"])
    names, variables, blocked = output_variables(pool, outputs, objective)
    emitter = Emitter(outputs, objective, names, request["solution_limit"])
    if isinstance(formula, WcnfFormula):
        if formula.soft_clauses():
            return optimise(formula, variables, blocked, emitter, deadline)
        return satisfy(formula.hard_clauses(), variables, blocked, emitter, deadline)
    return satisfy(formula.clauses(), variables, blocked, emitter, deadline)


if __name__ == "__main__":
    try:
        main()
    except BudgetExceeded as error:
        # SIGALRM fired while the submission was still building, or while a
        # solver was being waited on. Either way the budget ran out.
        finish("timeout", str(error))
    except Exception as error:
        traceback.print_exc(file=sys.stderr)
        finish("error", str(error))
    finally:
        # Descriptor 1 back to the protocol, and the saved copy closed, for a
        # program that runs this runner in its own process and reads on after.
        _PROTOCOL.flush()
        os.dup2(_PROTOCOL.fileno(), 1)
        _PROTOCOL.close()
        sys.stdout = _STDOUT
