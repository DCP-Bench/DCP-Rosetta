"""Readiness checks for the ortools_cp_sat_python integration and its current image.

Drives the repository evaluator against real containers, prints a JSON object
mapping check name to Boolean on stdout, and exits nonzero if any check failed.
`python -m generation.readiness check --solver ortools_cp_sat_python` runs this
and keeps its output as the readiness evidence.
"""
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from evaluation import evaluate, improving_incumbents
from evaluation.execution import image_identity
from evaluation.results import EvaluationError

SOLVER = "ortools_cp_sat_python"

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

GOOD = ("from ortools.sat.python import cp_model\n"
        "def build(instance):\n"
        "    n = instance['n']\n"
        "    model = cp_model.CpModel()\n"
        "    x, y = model.new_int_var(0, n, 'x'), model.new_int_var(0, n, 'y')\n"
        "    model.add(x + y == n)\n"
        "    return model, {'x': x, 'y': y}\n")
OPTIMAL = ("from ortools.sat.python import cp_model\n"
           "def build(instance):\n"
           "    n = instance['n']\n"
           "    model = cp_model.CpModel()\n"
           "    x, y = model.new_int_var(0, n, 'x'), model.new_int_var(0, n, 'y')\n"
           "    model.add(x + y >= n)\n"
           "    model.OBJECTIVE(x + y)\n"
           "    return model, {'x': x, 'y': y}\n")
MALFORMED = "def build(instance):\n    return None, {}\n"
UNSATISFIABLE = ("from ortools.sat.python import cp_model\n"
                 "def build(instance):\n"
                 "    model = cp_model.CpModel()\n"
                 "    x = model.new_int_var(0, 1, 'x')\n"
                 "    model.add(x == 0)\n"
                 "    model.add(x == 1)\n"
                 "    return model, {'x': x, 'y': 2}\n")
SLOW = "import time\ndef build(instance):\n    time.sleep(120)\n"
ISOLATED = ("import os, socket\n"
            "from ortools.sat.python import cp_model\n"
            "def build(instance):\n"
            "    assert os.getuid() != 0, 'container runs as root'\n"
            "    assert sorted(os.listdir('/input')) == ['model.py', 'request.json'], 'unexpected /input'\n"
            "    assert not os.path.exists('/dataset'), 'dataset is visible to the candidate'\n"
            "    probe = socket.socket()\n"
            "    probe.settimeout(0.5)\n"
            "    assert probe.connect_ex(('1.1.1.1', 443)) != 0, 'network reachable'\n"
            "    try:\n"
            "        open('/input/written', 'w')\n"
            "        raise AssertionError('input is writable')\n"
            "    except OSError:\n"
            "        pass\n"
            "    n = instance['n']\n"
            "    model = cp_model.CpModel()\n"
            "    x, y = model.new_int_var(0, n, 'x'), model.new_int_var(0, n, 'y')\n"
            "    model.add(x + y == n)\n"
            "    return model, {'x': x, 'y': y}\n")

# objective_values: every reported objective is the problem's own value. A maximisation whose objective has a
# constant term, with three optima (so the solutions enumerated at the optimum carry it too), and a
# minimisation with a negative optimum. CP-SAT keeps a maximisation negated, its constant as an offset.
OBJECTIVE_MAX_REF = """
# Data
n = 2
# End of data
import cpmpy as cp
import json
x = cp.intvar(0, n, name="x")
y = cp.intvar(0, n, name="y")
model = cp.Model(x + y <= n)
model.maximize(3 + x + y)
model.solve()
solution = {"x": int(x.value()), "y": int(y.value())}
print(json.dumps(solution))
"""
OBJECTIVE_MIN_REF = OBJECTIVE_MAX_REF.replace("x + y <= n", "x + y >= 1").replace(
    "model.maximize(3 + x + y)", "model.minimize(x - 2 * y - 4)")
OBJECTIVE_MAX = ("from ortools.sat.python import cp_model\n"
                 "def build(instance):\n"
                 "    n = instance['n']\n"
                 "    model = cp_model.CpModel()\n"
                 "    x, y = model.new_int_var(0, n, 'x'), model.new_int_var(0, n, 'y')\n"
                 "    model.add(x + y <= n)\n"
                 "    model.maximize(3 + x + y)\n"
                 "    return model, {'x': x, 'y': y}\n")
OBJECTIVE_MIN = OBJECTIVE_MAX.replace("x + y <= n", "x + y >= 1").replace(
    "model.maximize(3 + x + y)", "model.minimize(x - 2 * y - 4)")

# incumbents, incumbents_maximize: a small knapsack on which CP-SAT (one worker) finds
# three improving solutions before its proof: packed value 6, 14, 19 maximised, and the value left behind
# 19, 11, 6 minimised (sum(values) - packed, a constant CP-SAT keeps as an offset). Each incumbent is
# strictly better and the last the optimum.
KNAPSACK_REF = """
# Data
capacity = 16
# End of data
import cpmpy as cp
import json
weights = [3, 10, 6, 13]
values = [2, 7, 12, 4]
x = cp.boolvar(shape=4, name="x")
model = cp.Model(cp.sum(x * weights) <= capacity)
model.DIRECTION(OBJECTIVE)
model.solve()
solution = {"x": [bool(v) for v in x.value()]}
print(json.dumps(solution))
"""
KNAPSACK = ("from ortools.sat.python import cp_model\n"
            "def create_model(instance):\n"
            "    weights = [3, 10, 6, 13]\n"
            "    values = [2, 7, 12, 4]\n"
            "    model = cp_model.CpModel()\n"
            "    x = [model.new_bool_var(f'x{i}') for i in range(4)]\n"
            "    model.add(sum(w * b for w, b in zip(weights, x)) <= instance['capacity'])\n"
            "    model.DIRECTION(OBJECTIVE)\n"
            "    return model, {'x': x}\n")
LEFT_BEHIND = ("minimize", "sum(values) - sum(v * b for v, b in zip(values, x))")
PACKED = ("maximize", "sum(v * b for v, b in zip(values, x))")
REFERENCE_OBJECTIVES = {LEFT_BEHIND: "sum(values) - cp.sum(x * values)", PACKED: "cp.sum(x * values)"}


def knapsack(source, direction, objective):
    if source is KNAPSACK_REF:
        objective = REFERENCE_OBJECTIVES[(direction, objective)]
    return source.replace("DIRECTION", direction).replace("OBJECTIVE", objective)


# standalone_block: the entrypoint named create_model, and a standalone run block at the
# end that would fail if the runner executed it (it reads a file named on the command line).
STANDALONE = GOOD.replace("def build(", "def create_model(") + (
    "\n\nif __name__ == '__main__':\n"
    "    import json\n"
    "    import sys\n"
    "    instances = json.load(open(sys.argv[1]))\n"
    "    model, outputs = create_model(instances[0])\n"
    "    print(outputs)\n")


def main():
    results = {}
    with tempfile.TemporaryDirectory(prefix="dcp_readiness_") as directory:
        temp = Path(directory)

        def candidate(name, source):
            path = temp / name
            path.write_text(source, encoding="utf-8")
            return path

        def check(name, source, reference=REFERENCE, expected=None, **kwargs):
            result = evaluate(candidate(f"{name}.py", source), "readiness", SOLVER,
                              reference_source=reference, **kwargs)
            results[name] = result["accepted"] if expected is None else (
                not result["accepted"] and result["reason"] in expected)
            return result

        check("satisfaction", GOOD)
        check("changed_instances", GOOD, instances=[{"n": 3, "optimize": False}], instance_count=2)
        check("enumeration", GOOD, solution_limit=3)
        check("minimization", OPTIMAL.replace("OBJECTIVE", "minimize"), reference=OPTIMIZING)
        check("maximization", OPTIMAL.replace("OBJECTIVE", "maximize"), reference=MAXIMIZING)
        check("isolation", ISOLATED)
        check("malformed_output", MALFORMED, expected={"execution_error", "invalid_output"})
        check("empty_output", UNSATISFIABLE, expected={"no_solution"})
        check("timeout_cleanup", SLOW, expected={"execution_timeout"}, execution_timeout=2)
        check("standalone_block", STANDALONE)
        maximised = check("objective_values", OBJECTIVE_MAX, reference=OBJECTIVE_MAX_REF, solution_limit=3)
        minimised = check("objective_values", OBJECTIVE_MIN, reference=OBJECTIVE_MIN_REF)
        results["objective_values"] = (maximised["accepted"] and maximised["solutions_checked"] == 3
                                       and minimised["accepted"])
        # A CP-SAT solution callback reports each improving solution, in the problem's own terms.
        results["incumbents"] = improving_incumbents(
            check("incumbents", knapsack(KNAPSACK, *LEFT_BEHIND), reference=knapsack(KNAPSACK_REF, *LEFT_BEHIND)))
        results["incumbents_maximize"] = improving_incumbents(
            check("incumbents_maximize", knapsack(KNAPSACK, *PACKED), reference=knapsack(KNAPSACK_REF, *PACKED)),
            minimize=False)

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
