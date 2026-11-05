"""Readiness checks for the hermax integration and its current image.

Drives the repository evaluator against real containers, prints a JSON object
mapping check name to Boolean on stdout, and exits nonzero if any check failed.
`python -m generation.readiness check --solver hermax` runs this and keeps its
output as the readiness evidence.

The optimisation checks are the ones that matter here. A MaxSAT solver reaches
an answer long before it proves that answer best, and hermax reports the
difference through the solve status: `optimum` against `interrupted_sat`. The
runner emits a solution only on the former, so minimization and maximization
below are really checking that the objective the reference computes is the one
this integration reaches, in both directions.

`native_api` guards the mistake this integration was rebuilt to fix:
submissions have to be written against `hermax.model`, with the objective the
solver minimises on `model.obj`.

Runner protocol 2: an optimisation also returns its objective, in the problem's
own terms, which the runner decodes on each solution. `objective_values` checks
that the reported objective is the problem's value where the solver's cost is
not: a maximisation with a constant term (`3 + x + y`, whose cost on `model.obj`
is its complement) and a minimisation with a negative optimum (`x + y - 10`),
both accepted; `objective_required` that an optimisation without the objective
is refused; `objective_consistency` that an objective that differs between two
optima of the same cost ends the run with an error; and `objective_mismatch`
that the evaluator catches a scaled objective.

`memory_limit` checks that a model killed at the memory limit while it solves
ends as `memory_limit`, not as a solver error blamed on the model: hermax can
solve in a subprocess and report that subprocess's death as a bare `error` status.

`wide_output` declares a value above 2**32 as a sum of weighted Booleans, the
way a number too wide for one IntVar has to be written, and
`repeated_output_once` checks that two assignments reaching the same declared
total are reported as one solution.
"""
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from evaluation import evaluate
from evaluation.execution import image_identity
from evaluation.results import EvaluationError

SOLVER = "hermax"

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

HEAD = '''from hermax.model import Model


def build(instance):
    n = instance["n"]
    m = Model()
    x = m.int("x", 0, n)
    y = m.int("y", 0, n)
'''
EXPORT = '    return m, {"x": x, "y": y}\n'

GOOD = HEAD + "    m &= (x + y == n)\n" + EXPORT
# `n` is a maximum here, so the objective has room to move in both directions.
# COST is what the solver minimises, VALUE the problem's objective the runner reports.
OPTIMAL = (HEAD + "    m &= (x + y >= n)\n    m.obj += COST\n"
           '    return m, {"x": x, "y": y}, VALUE\n')


def optimal(cost, value):
    return OPTIMAL.replace("COST", cost).replace("VALUE", value)


MINIMIZING_MODEL = optimal("x + y", "x + y")
MAXIMIZING_MODEL = optimal("(2 * n) - (x + y)", "x + y")
# The problem's objective where the solver's cost differs from it: a constant
# term in a maximisation, and a negative minimum.
CONSTANT_REFERENCE = MAXIMIZING.replace("model.maximize(x + y)", "model.maximize(3 + x + y)")
CONSTANT_MODEL = optimal("(2 * n) - (x + y)", "3 + x + y")
NEGATIVE_REFERENCE = OPTIMIZING.replace("model.minimize(x + y)", "model.minimize(x + y - 10)")
NEGATIVE_MODEL = optimal("x + y", "x + y - 10")
# An optimisation without its objective, which the runner must refuse.
WITHOUT_OBJECTIVE = OPTIMAL.replace("COST", "x + y").replace(", VALUE", "")
# An objective that is not the one the soft clauses state: x alone differs between
# the optima of x + y, which all cost the same; 2 * (x + y) is scaled.
INCONSISTENT_MODEL = optimal("x + y", "x")
SCALED_MODEL = optimal("x + y", "2 * x + 2 * y")
# Solves, then corrupts the protocol stream the runner owns.
MALFORMED = (HEAD + "    m &= (x + y == n)\n"
             "    import os\n"
             "    os.write(1, b'this is not a protocol record\\n')\n" + EXPORT)
UNSATISFIABLE = HEAD + "    m &= (x == 0)\n    m &= (x == 1)\n" + EXPORT
# A random 3-SAT instance at the phase transition (4.26 clauses per variable) that
# the solver cannot settle in two seconds. The model has no soft clauses, so hermax
# hands it to Glucose 4.1 through PySAT. hermax 1.3.0 proves the pigeonhole used
# before (16 into 15 with all_different) unsat at once; 400 random variables still
# run past 20 seconds.
SLOW = (HEAD.replace("from hermax", "import random\nfrom hermax") + "    m &= (x + y == n)\n"
        "    rng = random.Random(7)\n"
        '    v = m.bool_vector("v", 400)\n'
        "    for _ in range(1704):\n"
        "        a, b, c = rng.sample(range(400), 3)\n"
        "        m &= ((v[a] if rng.random() < .5 else ~v[a]) | (v[b] if rng.random() < .5 else ~v[b])\n"
        "              | (v[c] if rng.random() < .5 else ~v[c]))\n" + EXPORT)

# hermax encodes an IntVar with one literal per value, so one over five million
# values passes a 256 MB limit while it is encoded. (hermax 1.3.0 needs far less
# memory for weighted soft units than 1.2.9, so the thousand used before no
# longer reach the limit.)
HUNGRY = (HEAD + "    m &= (x + y == n)\n"
          '    wide = m.int("wide", 0, 5_000_000)\n'
          "    m &= (wide >= 3)\n" + EXPORT)

# An output wider than any one IntVar could hold, declared as a sum of
# Booleans that the runner evaluates. 2**33 + n is above 32 bits.
WIDE_REFERENCE = '''
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
'''
WIDE = '''from hermax.model import Model


def build(instance):
    m = Model()
    bits = m.bool_vector("b", 35)
    total = sum(2 ** k * bits[k] for k in range(35))
    m &= (total == 2 ** 33 + instance["n"])
    return m, {"x": total}
'''
# Two assignments with the same declared total: the runner must report it once.
REPEAT_REFERENCE = '''
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
'''
REPEAT = '''from hermax.model import Model


def build(instance):
    m = Model()
    a = m.int("a", 0, 1)
    b = m.int("b", 0, 1)
    m &= (a + b == instance["n"])
    return m, {"x": a + b}
'''

ISOLATED = '''from hermax.model import Model


def build(instance):
    import os
    import socket

    def host_uid(uid):
        for line in open("/proc/self/uid_map"):
            inside, outside, count = map(int, line.split())
            if inside <= uid < inside + count:
                return outside + uid - inside

    # Unprivileged on the host: Docker runs as nobody; rootless podman without a
    # subuid range can only run as container root, which maps to the invoking user.
    assert os.getuid() != 0 or host_uid(0) != 0, "container runs as root on the host"
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
    m = Model()
    x = m.int("x", 0, n)
    y = m.int("y", 0, n)
    m &= (x + y == n)
    return m, {"x": x, "y": y}
'''

# The image must carry the framework itself and nothing standing in for it.
NATIVE = '''import hermax
from hermax.model import BoolVector, IntVar, IntVector, Model, sum_expr


def build(instance):
    assert hermax.__version__ == "1.3.0", hermax.__version__
    # 1.3.0 features the skill teaches.
    assert callable(sum_expr) and hasattr(IntVar, "piecewise")
    # The modelling layer the submissions are written against, not a wrapper
    # shipped alongside the runner.
    assert Model.__module__.startswith("hermax."), Model.__module__
    for absent in ("dcp_maxsat", "dcp_sat", "dcp_pb"):
        try:
            __import__(absent)
            raise AssertionError(f"{absent} is still installed in the image")
        except ImportError:
            pass
    probe = Model()
    assert isinstance(probe.int_vector("probe", 2, 0, 1), IntVector)
    assert isinstance(probe.bool_vector("flags", 2), BoolVector)

    n = instance["n"]
    m = Model()
    x = m.int("x", 0, n)
    y = m.int("y", 0, n)
    m &= (x + y == n)
    return m, {"x": x, "y": y}
'''


# standalone_block: the entrypoint named create_model, and a standalone run block at the
# end that would fail if the runner executed it (it reads a file named on the command line).
STANDALONE = GOOD.replace("def build(", "def create_model(") + (
    "\n\nif __name__ == '__main__':\n"
    "    import json\n"
    "    import sys\n"
    "    instances = json.load(open(sys.argv[1]))\n"
    "    model, outputs = create_model(instances[0])\n"
    "    result = model.solve()\n"
    "    print(outputs)\n")


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

        check("satisfaction", GOOD)
        check("changed_instances", GOOD, instances=[{"n": 3, "optimize": False}], instance_count=2)
        check("enumeration", GOOD, solution_limit=3)
        check("minimization", MINIMIZING_MODEL, reference=OPTIMIZING)
        check("maximization", MAXIMIZING_MODEL, reference=MAXIMIZING)
        check("objective_constant", CONSTANT_MODEL, reference=CONSTANT_REFERENCE)
        check("objective_negative", NEGATIVE_MODEL, reference=NEGATIVE_REFERENCE)
        results["objective_values"] = results.pop("objective_constant") and results.pop("objective_negative")
        check("objective_required", WITHOUT_OBJECTIVE, reference=OPTIMIZING, expected={"execution_error"})
        check("objective_consistency", INCONSISTENT_MODEL, reference=OPTIMIZING,
              expected={"execution_error"}, solution_limit=3)
        check("objective_mismatch", SCALED_MODEL, reference=OPTIMIZING, expected={"objective_mismatch"})
        check("native_api", NATIVE)
        check("wide_output", WIDE, reference=WIDE_REFERENCE)
        repeat = check("repeated_output_once", REPEAT, reference=REPEAT_REFERENCE,
                       solution_limit=2)
        results["repeated_output_once"] = (repeat["accepted"]
                                           and repeat["solutions_checked"] == 1)
        check("isolation", ISOLATED)
        check("malformed_output", MALFORMED, expected={"execution_error", "invalid_output"})
        check("empty_output", UNSATISFIABLE, expected={"no_solution"})
        check("timeout_cleanup", SLOW, expected={"execution_timeout"}, execution_timeout=2)
        # hermax reports a worker the kernel killed for memory as a plain solver
        # error; the evaluator has to see through that to the memory limit.
        check("memory_limit", HUNGRY, expected={"memory_limit"}, memory_mb=256)
        check("standalone_block", STANDALONE)

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
