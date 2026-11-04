"""Readiness checks for the Paramita (Python) integration and its current image.

Drives the repository evaluator against real containers, prints a JSON object
mapping check name to Boolean on stdout, and exits nonzero if any check failed.
`python -m generation.readiness check --solver paramita_python` runs this and
keeps its output as the readiness evidence.

Every candidate follows the contract in run.py: `create_model` returns
`(formula, pool), outputs`, a CnfFormula for satisfaction and a WcnfFormula,
whose soft clauses are the objective, for optimisation. MaxSAT maximises, so a
minimising candidate encodes the negated objective.

`minimization` and `maximization` check that the optimum the runner proves is
the one the reference computes, in both directions; `optimal_enumeration` that
every enumerated answer is optimal; `optima_exhausted` that enumeration stops at
the true number of optima and reports exhaustion; `wide_objective_enumeration`
that further optima are found for an objective over 2000 Bools;
`constant_objective` that a zero-weight objective is an optimisation in which
every solution is optimal; `suboptimal_rejected` that the evaluator still
catches a model that optimises the wrong direction; `optimization_timeout` that
an EvalMaxSAT search stopped at the budget ends as a timeout, never as an
answer. `rejects_third_value` and `wrong_container` check that the old forms
(an objective as a third value, constraints as a list, no pool) are refused.
`wcnf_without_soft` checks that a WcnfFormula without soft clauses is solved as
a satisfaction problem and enumerated in full, `free_output_bool` that an output
Bool the formula never mentions is enumerated both ways, and `empty_constraints`
that a formula without clauses is. `wide_output_rejected` checks that a total
beyond 32 bits that is not the answer is not accepted; `exact_wide_output` that
an integer output beyond 32 bits is read exactly, and `flat_sum` that a `sum`
over thousands of Bools does not exceed the recursion depth. `stray_stdout`
checks that the `c ...` lines EvalMaxSAT writes to standard output do not break
the protocol.

`native_api` guards against a modelling layer shipped beside the runner:
submissions are written against paramita itself.
"""
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from evaluation import evaluate
from evaluation.execution import image_identity
from evaluation.results import EvaluationError

SOLVER = "paramita_python"

# A tiny trusted reference, kept here so this script does not depend on the
# test suite. n=2 gives x+y==2 exactly three solutions.
REFERENCE = '''
# Data
n = 2
optimize = False
# End of data
import cpmpy as cp
import json
x = cp.intvar(0, n, name="x")
y = cp.intvar(0, n, name="y")
model = cp.Model(x + y >= n if optimize else x + y == n)
if optimize:
    model.minimize(x + y)
model.solve()
solution = {"x": int(x.value()), "y": y.value()}
print(json.dumps(solution))
'''
OPTIMIZING = REFERENCE.replace("optimize = False", "optimize = True")
MAXIMIZING = OPTIMIZING.replace("model.minimize", "model.maximize")

# x and y as unary sums of Bools, each with an order constraint so that the
# Bools form a unary number. Every candidate below starts from this prelude and
# ends with one of the encodings after it.
PRELUDE = """from paramita.containers import CnfFormula, WcnfFormula
from paramita.modelling import And, Bool, DimacsVariablePool, add_to_container, add_to_weighted_container, to_cnf


def unary(prefix, n):
    bits = [Bool(f"{prefix}{i}") for i in range(n)]
    order = [~bits[i + 1] | bits[i] for i in range(n - 1)]
    return sum(bits), order


def create_model(instance):
    n = instance["n"]
    x, order_x = unary("x", n)
    y, order_y = unary("y", n)
    subject = order_x + order_y
"""
OUTPUTS = '    outputs = {"x": x, "y": y}\n'
SATISFY = ("    formula, pool = CnfFormula(), DimacsVariablePool()\n"
           "    add_to_container(And(subject), to_cnf, formula, pool)\n"
           "    return (formula, pool), outputs\n")


def optimising(objective):
    """The encoding that maximises `objective` under the constraints."""
    return ("    formula, pool = WcnfFormula(), DimacsVariablePool()\n"
            f"    add_to_weighted_container({objective}, And(subject), to_cnf, formula, pool)\n"
            "    return (formula, pool), outputs\n")


GOOD = PRELUDE + "    subject.append(x + y == n)\n" + OUTPUTS + SATISFY
# x + y >= n, minimised (MaxSAT maximises the negation) or maximised.
MINIMIZING_MODEL = PRELUDE + "    subject.append(x + y >= n)\n" + OUTPUTS + optimising("-(x + y)")
MAXIMIZING_MODEL = PRELUDE + "    subject.append(x + y >= n)\n" + OUTPUTS + optimising("x + y")
# The old forms: an objective as a third value, constraints as a list, and a
# formula without its pool. The runner must refuse each rather than guess.
THIRD_VALUE = MINIMIZING_MODEL.replace("    return (formula, pool), outputs\n",
                                       '    return (formula, pool), outputs, ("minimize", x + y)\n')
AS_LIST = PRELUDE + "    subject.append(x + y == n)\n" + OUTPUTS + "    return subject, outputs\n"
NO_POOL = GOOD.replace("    return (formula, pool), outputs\n", "    return formula, outputs\n")
# A WcnfFormula without soft clauses: the objective 0 adds none, so it is a
# satisfaction problem with all three solutions of x + y == 2.
WCNF_WITHOUT_SOFT = PRELUDE + "    subject.append(x + y == n)\n" + OUTPUTS + optimising("0")
# A zero-weight objective adds a soft clause of weight 0: optimisation, in which
# all three solutions are optimal.
CONSTANT_OBJECTIVE = (PRELUDE + "    subject.append(x + y == n)\n" + OUTPUTS
                      + optimising("0 * x + 4"))
# An output Bool z the formula never mentions. The reference leaves z free, so
# there are six solutions, and the runner must find them all.
FREE_OUTPUT = (PRELUDE + "    subject.append(x + y == n)\n"
               '    outputs = {"x": x, "y": y, "z": Bool("z")}\n' + SATISFY)
FREE_REFERENCE = """
# Data
n = 2
# End of data
import cpmpy as cp
import json
x = cp.intvar(0, n, name="x")
y = cp.intvar(0, n, name="y")
z = cp.boolvar(name="z")
model = cp.Model(x + y == n)
model.solve()
solution = {"x": int(x.value()), "y": int(y.value()), "z": bool(z.value())}
print(json.dumps(solution))
"""
# No constraint at all: a formula without clauses, and one free output.
EMPTY_CONSTRAINTS = """from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool


def create_model(instance):
    return (CnfFormula(), DimacsVariablePool()), {"z": Bool("z")}
"""
EMPTY_REFERENCE = """
# Data
n = 2
# End of data
import cpmpy as cp
import json
z = cp.boolvar(name="z")
model = cp.Model(z | ~z)
model.solve()
solution = {"z": bool(z.value())}
print(json.dumps(solution))
"""
# Minimise x + y plus a weighted sum over 2000 more Bools, which the optimum
# sets false. The further optima over x and y are found by blocking, without
# encoding the wide objective at its optimum. (A cardinality constraint over the
# 2000 Bools, such as at least ten of them, is beyond EvalMaxSAT in two minutes.)
WIDE_OBJECTIVE = (PRELUDE + "    subject.append(x + y >= n)\n"
                  "    many = [Bool(f\"m{i}\") for i in range(2000)]\n" + OUTPUTS
                  + optimising("-(x + y + sum((1 + i % 10) * b for i, b in enumerate(many)))"))
# A pigeonhole of 18 pigeons in 17 holes, under the same unary x and y. It is
# unsatisfiable and, unlike 13 in 12, too hard for CaDiCaL to refute in two
# seconds, so the search is stopped at the budget.
PIGEONHOLE = """
    holes = [[Bool(f"p{i}_{j}") for j in range(17)] for i in range(18)]
    for row in holes:
        subject.append(sum(row) >= 1)
    for j in range(17):
        subject.append(sum(holes[i][j] for i in range(18)) <= 1)
"""
SLOW = PRELUDE + "    subject.append(x + y == n)\n" + PIGEONHOLE + OUTPUTS + SATISFY
SLOW_OPTIMAL = (PRELUDE + "    subject.append(x + y >= n)\n" + PIGEONHOLE + OUTPUTS
                + optimising("-(x + y)"))
# Contradictory hard units. EvalMaxSAT writes a `c ...` line to standard output
# while it loads them.
CONTRADICTION = (PRELUDE + "    a = Bool(\"a\")\n    subject.extend([a, ~a])\n"
                 + "    subject.append(x + y >= n)\n" + OUTPUTS + optimising("-(x + y)"))
# A candidate that returns an output the runner cannot read.
MALFORMED = (PRELUDE + "    subject.append(x + y == n)\n"
             + '    outputs = {"x": "not an expression", "y": y}\n' + SATISFY)
# One weighted PB equality over 2000 Bools besides x + y == n. The default
# encoder recurses once per term and overflowed the default stack (signal 11)
# until the runner raised its stack limit.
LARGE_PB = (PRELUDE + "    subject.append(x + y == n)\n"
            "    many = [Bool(f\"m{i}\") for i in range(2000)]\n"
            "    subject.append(sum((1 + i % 10) * b for i, b in enumerate(many)) == 1000)\n"
            + OUTPUTS + SATISFY)
UNSATISFIABLE = PRELUDE + "    subject.extend([x == 0, x == 1])\n" + OUTPUTS + SATISFY

# A total of at least 2**31 from two groups of 31 Bools. The reference asks for
# 2**33 + n, which no assignment reaches, so the evaluator must reject the output
# rather than accept it, whether the value arrives wrapped or exact.
WIDE_REFERENCE = """
# Data
n = 2
# End of data
import cpmpy as cp
import json
x = cp.intvar(0, 2 ** 34, name="x")
model = cp.Model(x == 2 ** 33 + n)
model.solve()
solution = {"x": int(x.value())}
print(json.dumps(solution))
"""
HEADER = """from paramita.containers import CnfFormula
from paramita.modelling import And, Bool, DimacsVariablePool, add_to_container, to_cnf


def encoded(constraint):
    formula, pool = CnfFormula(), DimacsVariablePool()
    add_to_container(constraint, to_cnf, formula, pool)
    return formula, pool
"""
WIDE = HEADER + """

def create_model(instance):
    low = [Bool(f"a{k}") for k in range(31)]
    high = [Bool(f"c{k}") for k in range(31)]
    total = sum(bit * 2 ** k for k, bit in enumerate(low)) + sum(bit * 2 ** k for k, bit in enumerate(high))
    return encoded(And([low[30], high[30]])), {"x": total}
"""
# Integer outputs are read in Python integers: two coefficients of 2 * 10**9
# each fit in 32 bits, and their sum, 4 * 10**9, must arrive exact, not wrapped.
EXACT_REFERENCE = WIDE_REFERENCE.replace("2 ** 33 + n", "4 * 10 ** 9")
EXACT = HEADER + """

def create_model(instance):
    a, b = Bool("a"), Bool("b")
    return encoded(And([a, b])), {"x": 2 * 10 ** 9 * a + 2 * 10 ** 9 * b}
"""
# A sum over 3000 Bools built with `sum`, a chain of 3000 nested additions,
# as an output and in a constraint. It exceeded Python's default recursion
# depth in the runner's expression walkers until the runner raised it.
FLAT_SUM = HEADER + """

def create_model(instance):
    many = [Bool(f"m{i}") for i in range(3000)]
    return encoded(sum(many) == 1500), {"x": sum(many)}
"""
FLAT_SUM_REFERENCE = WIDE_REFERENCE.replace("2 ** 33 + n", "1500")
REPEAT_REFERENCE = """
# Data
n = 1
# End of data
import cpmpy as cp
import json
x = cp.intvar(0, 2, name="x")
model = cp.Model(x == n)
model.solve()
solution = {"x": int(x.value())}
print(json.dumps(solution))
"""
# Two assignments with the same declared total: the runner must report it once.
REPEAT = HEADER + """

def create_model(instance):
    a = Bool("a")
    b = Bool("b")
    return encoded(a + b == instance["n"]), {"x": a + b}
"""

ISOLATED = HEADER + """

def create_model(instance):
    import os
    import socket

    assert os.getuid() != 0, "container runs as root"
    assert not os.path.exists("/dataset"), "dataset is visible to the candidate"
    assert sorted(os.listdir("/input")) == ["model.py", "request.json"], "unexpected /input"
    try:
        open("/input/written", "w")
        raise AssertionError("input is writable")
    except OSError:
        pass
    probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    probe.settimeout(0.5)
    try:
        probe.connect(("1.1.1.1", 443))
        raise AssertionError("network reachable")
    except OSError:
        pass
    finally:
        probe.close()

    n = instance["n"]
    x = sum(Bool(f"x{i}") for i in range(n))
    y = sum(Bool(f"y{i}") for i in range(n))
    return encoded(x + y == n), {"x": x, "y": y}
"""

# The image must carry paramita itself and nothing standing in for it.
NATIVE = HEADER + """
import paramita
from paramita.containers import WcnfFormula
from paramita.solvers import MaxSatSolver, SatSolver


def create_model(instance):
    # The classes a submission builds with, all from the framework.
    for cls in (Bool, CnfFormula, WcnfFormula, DimacsVariablePool, SatSolver, MaxSatSolver):
        assert cls.__module__.startswith("paramita"), cls.__module__
    for absent in ("dcp_sat", "dcp_maxsat", "dcp_pb"):
        try:
            __import__(absent)
            raise AssertionError(f"{absent} is still installed in the image")
        except ImportError:
            pass

    n = instance["n"]
    x = sum(Bool(f"x{i}") for i in range(n))
    y = sum(Bool(f"y{i}") for i in range(n))
    return encoded(x + y == n), {"x": x, "y": y}
"""


def main():
    results = {}
    with tempfile.TemporaryDirectory(prefix="dcp_readiness_") as directory:
        temp = Path(directory)

        def candidate(name, source):
            path = temp / f"{name}.py"
            path.write_text(source, encoding="utf-8")
            return path

        def check(name, source, reference=REFERENCE, expected=None, **kwargs):
            result = evaluate(candidate(name, source), "readiness", SOLVER,
                              reference_source=reference, **kwargs)
            results[name] = result["accepted"] if expected is None else (
                not result["accepted"] and result["reason"] in expected)
            return result

        def runner_status(result):
            return result["instances"][0].get("runner_status", {}).get("status") if result["instances"] else None

        def exhausted(name, result, count):
            """Accepted, `count` distinct solutions, and exhaustion reported."""
            results[name] = (result["accepted"] and result["solutions_checked"] == count
                             and runner_status(result) == "complete")

        check("satisfaction", GOOD)
        check("changed_instances", GOOD, instances=[{"n": 3, "optimize": False}], instance_count=2)
        exhausted("enumeration", check("enumeration", GOOD, solution_limit=5), 3)
        check("minimization", MINIMIZING_MODEL, reference=OPTIMIZING)
        check("maximization", MAXIMIZING_MODEL, reference=MAXIMIZING)
        optimal = check("optimal_enumeration", MINIMIZING_MODEL, reference=OPTIMIZING, solution_limit=3)
        results["optimal_enumeration"] = (optimal["accepted"] and optimal["solutions_checked"] == 3)
        exhausted("optima_exhausted",
                  check("optima_exhausted", MINIMIZING_MODEL, reference=OPTIMIZING, solution_limit=5), 3)
        wide = check("wide_objective_enumeration", WIDE_OBJECTIVE, reference=OPTIMIZING,
                     solution_limit=2, execution_timeout=120)
        results["wide_objective_enumeration"] = (wide["accepted"] and wide["solutions_checked"] == 2)
        exhausted("constant_objective", check("constant_objective", CONSTANT_OBJECTIVE, solution_limit=5), 3)
        check("suboptimal_rejected", MAXIMIZING_MODEL, reference=OPTIMIZING,
              expected={"suboptimal_solution"})
        check("rejects_third_value", THIRD_VALUE, reference=OPTIMIZING, expected={"execution_error"})
        check("wrong_container_list", AS_LIST, expected={"execution_error"})
        check("wrong_container_pool", NO_POOL, expected={"execution_error"})
        results["wrong_container"] = (results.pop("wrong_container_list")
                                      and results.pop("wrong_container_pool"))
        exhausted("wcnf_without_soft", check("wcnf_without_soft", WCNF_WITHOUT_SOFT, solution_limit=5), 3)
        exhausted("free_output_bool",
                  check("free_output_bool", FREE_OUTPUT, reference=FREE_REFERENCE, solution_limit=10), 6)
        exhausted("empty_constraints",
                  check("empty_constraints", EMPTY_CONSTRAINTS, reference=EMPTY_REFERENCE, solution_limit=5), 2)
        check("optimization_timeout", SLOW_OPTIMAL, reference=OPTIMIZING,
              expected={"execution_timeout"}, execution_timeout=2)
        check("stray_stdout", CONTRADICTION, reference=OPTIMIZING, expected={"no_solution"})
        check("native_api", NATIVE)
        check("wide_output_rejected", WIDE, reference=WIDE_REFERENCE,
              expected={"invalid_output", "invalid_solution", "no_solution"})
        check("exact_wide_output", EXACT, reference=EXACT_REFERENCE)
        check("flat_sum", FLAT_SUM, reference=FLAT_SUM_REFERENCE, execution_timeout=120)
        repeat = check("repeated_output_once", REPEAT, reference=REPEAT_REFERENCE, solution_limit=2)
        results["repeated_output_once"] = (repeat["accepted"] and repeat["solutions_checked"] == 1)
        check("isolation", ISOLATED)
        check("malformed_output", MALFORMED, expected={"execution_error", "invalid_output"})
        check("empty_output", UNSATISFIABLE, expected={"no_solution"})
        check("large_pb_constraint", LARGE_PB, execution_timeout=120)
        check("timeout_cleanup", SLOW, expected={"execution_timeout"}, execution_timeout=2)

    try:
        image_identity({"id": SOLVER, "image": "dcp-eval/definitely-absent:readiness"})
        results["missing_image"] = False
    except EvaluationError as error:
        results["missing_image"] = error.reason == "infrastructure_error"

    print(json.dumps(results, sort_keys=True))
    if not all(results.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
