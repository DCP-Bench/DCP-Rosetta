"""Readiness checks for the hexaly_python integration and its current image.

Drives the repository evaluator against real containers, prints a JSON object
mapping check name to Boolean on stdout, and exits nonzero if any check failed.
`python -m generation.readiness check --solver hexaly_python` runs this and
keeps its output as the readiness evidence. Every solving check needs the Hexaly
licence configured on this machine (`python -m evaluation.licences check hexaly`);
`licence_missing` runs the solver without it.
"""
import json
import os
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from evaluation import evaluate
from evaluation.execution import image_identity
from evaluation.results import EvaluationError

SOLVER = "hexaly_python"

# A tiny trusted reference, kept here so this script does not depend on the
# test suite. n=2 gives x+y==2 exactly three solutions, and x+y>=2 under
# minimization exactly three optima.
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

HEADER = ("import hexaly.optimizer as hx\n\n\n"
          "def build(instance):\n"
          "    n = instance['n']\n"
          "    optimizer = hx.HexalyOptimizer()\n"
          "    model = optimizer.model\n")
XY = "    x = model.int(0, n)\n    y = model.int(0, n)\n"
GOOD = HEADER + XY + ("    model.constraint(x + y == n)\n"
                      "    return optimizer, {'x': x, 'y': y}\n")
OPTIMAL = HEADER + XY + ("    model.constraint(x + y >= n)\n"
                         "    model.OBJECTIVE(x + y)\n"
                         "    return optimizer, {'x': x, 'y': y}\n")
# objective_values: every objective the runner reports is the problem's own value. A maximisation with a constant
# term and a minimisation with a negative optimum; accepted means the runner reported exactly the optimum, 7 and -5.
CONSTANT_MAXIMUM = OPTIMIZING.replace("model.minimize(x + y)", "model.maximize(3 + x + y)")
NEGATIVE_MINIMUM = OPTIMIZING.replace("model.minimize(x + y)", "model.minimize(x - y - 3)")
CONSTANT_OPTIMAL = OPTIMAL.replace("OBJECTIVE(x + y)", "maximize(3 + x + y)")
NEGATIVE_OPTIMAL = OPTIMAL.replace("OBJECTIVE(x + y)", "minimize(x - y - 3)")
MALFORMED = "def build(instance):\n    return None, {}\n"
# Presolve proves this one: the only proof of infeasibility Hexaly gives.
UNSATISFIABLE = HEADER + ("    x = model.int(0, 1)\n"
                          "    model.constraint(x >= 2)\n"
                          "    return optimizer, {'x': x, 'y': 2}\n")
SLOW = "import time\n\n\ndef build(instance):\n    time.sleep(120)\n"
ISOLATED = HEADER.replace("    optimizer = hx", (
    "    import os, socket\n"
    "    assert os.getuid() != 0, 'container runs as root'\n"
    "    assert sorted(os.listdir('/input')) == ['model.py', 'request.json'], 'unexpected /input'\n"
    "    assert not os.path.exists('/dataset'), 'dataset is visible to the candidate'\n"
    "    probe = socket.socket()\n"
    "    probe.settimeout(0.5)\n"
    "    assert probe.connect_ex(('1.1.1.1', 443)) != 0, 'network reachable'\n"
    "    optimizer = hx")) + XY + ("    model.constraint(x + y == n)\n"
                                  "    return optimizer, {'x': x, 'y': y}\n")


# ---------------------------------------------------------------------------
# Bug-class checks (readiness level 2). Each pairs a tiny trusted reference with a
# submission that exercises one class of runner bug the modelling campaigns found.

# optimization_timeout: the reference is easy (minimise x, optimum n); the submission
# adds an 11-mark Golomb ruler to its objective, so Hexaly finds a solution at once
# but cannot prove the optimum within the budget. A correct runner emits nothing.
EASY_MIN = """
# Data
n = 2
# End of data
import cpmpy as cp
import json
x = cp.intvar(0, 10, name="x")
model = cp.Model(x >= n)
model.minimize(x)
model.solve()
solution = {"x": int(x.value())}
print(json.dumps(solution))
"""
UNPROVABLE = HEADER + ("    x = model.int(0, 10)\n"
                       "    marks = [model.int(0, 200) for _ in range(11)]\n"
                       "    diffs = [marks[j] - marks[i] for i in range(11) for j in range(i + 1, 11)]\n"
                       "    model.constraint(x >= n)\n"
                       "    model.constraint(marks[0] == 0)\n"
                       "    for i in range(10):\n"
                       "        model.constraint(marks[i] < marks[i + 1])\n"
                       "    model.constraint(model.count(model.distinct(model.array(diffs))) == len(diffs))\n"
                       "    model.minimize(1000 * x + marks[10])\n"
                       "    return optimizer, {'x': x}\n")
# minimization_step_one: the optimum sits one below an easy solution. Hexaly proves
# optima itself and the runner never bounds the objective, so this guards the pin.
STEP_REF = EASY_MIN.replace("x >= n", "x >= n - 1")
STEP = HEADER + ("    x = model.int(0, 10)\n"
                 "    model.constraint(x >= n - 1)\n"
                 "    model.minimize(x)\n"
                 "    return optimizer, {'x': x}\n")
# optimum_enumeration: a compound objective (a sum) with ten optimal solutions.
SUM_REF = """
# Data
n = 2
# End of data
import cpmpy as cp
import json
x = cp.intvar(0, 2, shape=4, name="x")
model = cp.Model(cp.sum(x) >= n)
model.minimize(cp.sum(x))
model.solve()
solution = {"x": x.value().tolist()}
print(json.dumps(solution))
"""
SUM = HEADER + ("    x = [model.int(0, 2) for _ in range(4)]\n"
                "    model.constraint(model.sum(x) >= n)\n"
                "    model.minimize(model.sum(x))\n"
                "    return optimizer, {'x': x}\n")
# output_shapes: a three-level integer array, a Boolean matrix and a value beyond 32 bits.
SHAPES_REF = """
# Data
n = 2
# End of data
import cpmpy as cp
import json
cube = cp.intvar(0, 10, shape=(2, 2, 2), name="cube")
grid = cp.boolvar(shape=(2, 2), name="grid")
big = cp.intvar(0, 40000000000, name="big")
model = cp.Model([cube[i, j, k] == i + j + k + n for i in range(2) for j in range(2) for k in range(2)],
                 [grid[i, j] == (i == j) for i in range(2) for j in range(2)],
                 big == 30000000000 + n)
model.solve()
solution = {"cube": cube.value().tolist(), "grid": grid.value().tolist(), "big": int(big.value())}
print(json.dumps(solution))
"""
SHAPES = HEADER + ("    cube = [[[model.int(0, 10) for k in range(2)] for j in range(2)] for i in range(2)]\n"
                   "    grid = [[model.bool() for j in range(2)] for i in range(2)]\n"
                   "    big = model.int(0, 40000000000)\n"
                   "    for i in range(2):\n"
                   "        for j in range(2):\n"
                   "            model.constraint(grid[i][j] == int(i == j))\n"
                   "            for k in range(2):\n"
                   "                model.constraint(cube[i][j][k] == i + j + k + n)\n"
                   "    model.constraint(big == 30000000000 + n)\n"
                   "    return optimizer, {'cube': cube, 'grid': grid, 'big': big}\n")
# instance_shapes: ragged rows, rows of mixed types, a string field the model ignores,
# and name/note keys, on two instances with different shapes.
SHAPED_REF = """
# Data
n = 2
rows = [[1], [2, 3]]
mixed = [[1, "a"], [2, "b"]]
label = "first"
# End of data
import cpmpy as cp
import json
total = cp.intvar(0, 1000, name="total")
key = cp.intvar(0, 1000, name="key")
model = cp.Model(total == n + sum(sum(row) for row in rows), key == sum(row[0] for row in mixed))
model.solve()
solution = {"total": int(total.value()), "key": int(key.value())}
print(json.dumps(solution))
"""
SHAPED_INSTANCE = {"n": 3, "rows": [[4, 5, 6], [], [1]], "mixed": [[3, "c"]], "label": "second",
                   "name": "readiness", "note": "ragged rows, mixed rows, an unused string"}
SHAPED = HEADER + ("    total = model.int(0, 1000)\n"
                   "    key = model.int(0, 1000)\n"
                   "    model.constraint(total == n + sum(sum(row) for row in instance['rows']))\n"
                   "    model.constraint(key == sum(row[0] for row in instance['mixed']))\n"
                   "    return optimizer, {'total': total, 'key': key}\n")
# error_detail: the library raises while the model is built; the evaluator must report
# execution_error with Hexaly's own message, not a timeout or a bare exit code.
FAILING = HEADER + ("    x = model.int(n, 0)\n"
                    "    return optimizer, {'x': x, 'y': x}\n")
# stray_stdout: the module, the submission and Hexaly's log all write to stdout.
CHATTY = HEADER.replace("    optimizer = hx", (
    "    import os\n"
    "    print('building for n =', n)\n"
    "    os.write(1, b'noise on fd 1\\n')\n"
    "    optimizer = hx")).replace("import hexaly", "print('loading the model')\nimport hexaly") + XY + (
    "    optimizer.param.verbosity = 2\n"
    "    model.constraint(x + y == n)\n"
    "    return optimizer, {'x': x, 'y': y}\n")
# auxiliary_free_distinct: a free auxiliary variable must not repeat output solutions.
AUXILIARY = HEADER + XY + ("    spare = model.int(0, 5)\n"
                           "    model.constraint(x + y == n)\n"
                           "    model.constraint(spare >= 0)\n"
                           "    return optimizer, {'x': x, 'y': y}\n")
# large_model: 3000 Booleans in one sum, reported as an output.
LARGE_REF = """
# Data
n = 1500
# End of data
import cpmpy as cp
import json
b = cp.boolvar(shape=3000, name="b")
count = cp.intvar(0, 3000, name="count")
model = cp.Model(count == cp.sum(b), count == n)
model.solve()
solution = {"b": b.value().tolist(), "count": int(count.value())}
print(json.dumps(solution))
"""
LARGE = HEADER + ("    b = [model.bool() for _ in range(3000)]\n"
                  "    count = model.int(0, 3000)\n"
                  "    model.constraint(count == model.sum(b))\n"
                  "    model.constraint(count == n)\n"
                  "    return optimizer, {'b': b, 'count': count}\n")


# ---------------------------------------------------------------------------
# Hexaly-specific checks.

# A list decision and a nested array as outputs, enumerated: three permutations of
# 0..2 and three 2x2 0/1 grids with n ones, each read back and excluded as a whole.
PERM_REF = """
# Data
n = 2
# End of data
import cpmpy as cp
import json
perm = cp.intvar(0, 2, shape=3, name="perm")
grid = cp.intvar(0, 1, shape=(2, 2), name="grid")
model = cp.Model(cp.AllDifferent(perm), cp.sum(grid) == n)
model.solve()
solution = {"perm": perm.value().tolist(), "grid": grid.value().tolist()}
print(json.dumps(solution))
"""
PERM = HEADER + ("    perm = model.list(3)\n"
                 "    model.constraint(model.count(perm) == 3)\n"
                 "    cells = [[model.int(0, 1) for j in range(2)] for i in range(2)]\n"
                 "    model.constraint(model.sum(c for row in cells for c in row) == n)\n"
                 "    return optimizer, {'perm': perm, 'grid': model.array(cells)}\n")
# 3-queens has no solution and Hexaly's search cannot prove it: a timeout, never unsat.
QUEENS_REF = """
# Data
n = 2
# End of data
import cpmpy as cp
import json
x = cp.intvar(0, 2, shape=3, name="q")
model = cp.Model(cp.AllDifferent(x))
model.solve()
solution = {"q": x.value().tolist()}
print(json.dumps(solution))
"""
QUEENS = HEADER + ("    q = [model.int(0, 2) for _ in range(3)]\n"
                   "    for i in range(3):\n"
                   "        for j in range(i + 1, 3):\n"
                   "            model.constraint(q[i] != q[j])\n"
                   "            model.constraint(q[i] + i != q[j] + j)\n"
                   "            model.constraint(q[i] - i != q[j] - j)\n"
                   "    return optimizer, {'q': q}\n")
# ft06 (optimum 55) as intervals and one list per machine. With one or two threads
# Hexaly's bound stays at 54; with four it is proven in under 2 s. The submission asks
# for one thread, so only a runner that forces four gets the proof within the budget.
FT06 = [[[2, 1], [0, 3], [1, 6], [3, 7], [5, 3], [4, 6]],
        [[1, 8], [2, 5], [4, 10], [5, 10], [0, 10], [3, 4]],
        [[2, 5], [3, 4], [5, 8], [0, 9], [1, 1], [4, 7]],
        [[1, 5], [0, 5], [2, 5], [3, 3], [4, 8], [5, 9]],
        [[2, 9], [1, 3], [4, 5], [5, 4], [0, 3], [3, 1]],
        [[1, 3], [3, 3], [5, 9], [0, 10], [4, 4], [2, 1]]]
FT06_REF = f"""
# Data
jobs = {FT06!r}
# End of data
import cpmpy as cp
import json
horizon = sum(d for job in jobs for _, d in job)
start = cp.intvar(0, horizon, shape=(6, 6), name="start")
makespan = cp.intvar(0, horizon, name="makespan")
model = cp.Model()
for j, job in enumerate(jobs):
    for k in range(1, 6):
        model += start[j, k - 1] + job[k - 1][1] <= start[j, k]
    model += start[j, 5] + job[5][1] <= makespan
for m in range(6):
    tasks = [(j, k) for j in range(6) for k in range(6) if jobs[j][k][0] == m]
    model += cp.NoOverlap([start[j, k] for j, k in tasks], [jobs[j][k][1] for j, k in tasks],
                          [start[j, k] + jobs[j][k][1] for j, k in tasks])
model.minimize(makespan)
model.solve()
solution = {{"makespan": int(makespan.value())}}
print(json.dumps(solution))
"""
FT06_MODEL = '''import hexaly.optimizer as hx


def build(instance):
    jobs = instance["jobs"]
    optimizer = hx.HexalyOptimizer()
    optimizer.param.nb_threads = 1
    model = optimizer.model
    horizon = sum(d for job in jobs for _, d in job)
    task = [[model.interval(0, horizon) for _ in job] for job in jobs]
    for j, job in enumerate(jobs):
        for k, (_, d) in enumerate(job):
            model.constraint(model.length(task[j][k]) == d)
            if k:
                model.constraint(task[j][k - 1] < task[j][k])
    for m in range(1 + max(mm for job in jobs for mm, _ in job)):
        on_m = [task[j][k] for j, job in enumerate(jobs) for k, (mm, _) in enumerate(job) if mm == m]
        tasks_m = model.array(on_m)
        order = model.list(len(on_m))
        model.constraint(model.count(order) == len(on_m))
        follows = model.lambda_function(lambda i: tasks_m[order[i]] < tasks_m[order[i + 1]])
        model.constraint(model.and_(model.range(0, len(on_m) - 1), follows))
    makespan = model.max(model.end(job[-1]) for job in task)
    model.minimize(makespan)
    return optimizer, {"makespan": makespan}
'''
# Outputs the runner must refuse with Hexaly's reason rather than coerce.
FLOAT = HEADER + XY + ("    model.constraint(x + y == n)\n"
                       "    return optimizer, {'x': x / 1, 'y': y}\n")
SET = HEADER + XY + ("    s = model.set(3)\n"
                     "    model.constraint(x + y == n)\n"
                     "    return optimizer, {'x': x, 'y': s}\n")
# A submission that builds inside a with-block hands back a deleted optimizer.
WITH_BLOCK = ("import hexaly.optimizer as hx\n\n\n"
              "def build(instance):\n"
              "    n = instance['n']\n"
              "    with hx.HexalyOptimizer() as optimizer:\n"
              "        model = optimizer.model\n"
              "        x = model.int(0, n)\n"
              "        y = model.int(0, n)\n"
              "        model.constraint(x + y == n)\n"
              "    return optimizer, {'x': x, 'y': y}\n")


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

        def exhausts(name, result, count):
            first = result["instances"][0] if result["instances"] else {}
            results[name] = (results[name] and first.get("solutions_received") == count
                             and first.get("runner_status", {}).get("status") == "complete")

        def says(name, result, text):
            results[name] = results[name] and text in json.dumps(result)

        check("satisfaction", GOOD)
        check("changed_instances", GOOD, instances=[{"n": 3, "optimize": False}], instance_count=2)
        check("enumeration", GOOD, solution_limit=3)
        check("minimization", OPTIMAL.replace("OBJECTIVE", "minimize"), reference=OPTIMIZING)
        check("maximization", OPTIMAL.replace("OBJECTIVE", "maximize"), reference=MAXIMIZING)
        results["objective_values"] = all(
            check("objective_values", source, reference=reference)["accepted"]
            for source, reference in ((CONSTANT_OPTIMAL, CONSTANT_MAXIMUM), (NEGATIVE_OPTIMAL, NEGATIVE_MINIMUM)))
        check("isolation", ISOLATED)
        check("malformed_output", MALFORMED, expected={"execution_error", "invalid_output"})
        check("empty_output", UNSATISFIABLE, expected={"no_solution"})
        check("timeout_cleanup", SLOW, expected={"execution_timeout"}, execution_timeout=2)

        # Bug-class checks (readiness level 2).
        result = evaluate(candidate("optimization_timeout.py", UNPROVABLE), "readiness", SOLVER,
                          reference_source=EASY_MIN, execution_timeout=3)
        results["optimization_timeout"] = (result["reason"] == "execution_timeout"
                                           and all(item.get("solutions_received", 0) == 0
                                                   for item in result["instances"]))
        check("minimization_step_one", STEP, reference=STEP_REF)
        result = check("optimum_enumeration", SUM, reference=SUM_REF, solution_limit=3)
        results["optimum_enumeration"] = result["accepted"] and result["solutions_checked"] == 3
        check("output_shapes", SHAPES, reference=SHAPES_REF)
        check("instance_shapes", SHAPED, reference=SHAPED_REF, instances=[SHAPED_INSTANCE], instance_count=2)
        says("error_detail", check("error_detail", FAILING, expected={"execution_error"}),
             "Int boundaries are inconsistent")
        check("stray_stdout", CHATTY)
        result = check("auxiliary_free_distinct", AUXILIARY, solution_limit=3)
        results["auxiliary_free_distinct"] = result["accepted"] and result["solutions_checked"] == 3
        check("large_model", LARGE, reference=LARGE_REF, execution_timeout=120, reference_timeout=120)

        # Hexaly-specific checks.
        # x+y==2 has three solutions; soft no-goods must prove there is no fourth.
        exhausts("exhausted_enumeration", check("exhausted_enumeration", GOOD, solution_limit=5), 3)
        exhausts("optimal_enumeration", check("optimal_enumeration", OPTIMAL.replace("OBJECTIVE", "minimize"),
                                              reference=OPTIMIZING, solution_limit=5), 3)
        result = check("collection_outputs", PERM, reference=PERM_REF, solution_limit=3)
        results["collection_outputs"] = result["accepted"] and result["solutions_checked"] == 3
        check("unproven_infeasibility", QUEENS, reference=QUEENS_REF, expected={"execution_timeout"},
              execution_timeout=5)
        check("bound_threads", FT06_MODEL, reference=FT06_REF, execution_timeout=60, reference_timeout=120)
        says("float_output", check("float_output", FLOAT, expected={"execution_error"}), "float expression")
        says("set_output", check("set_output", SET, expected={"execution_error"}), "is a set")
        check("with_block", WITH_BLOCK, expected={"execution_error"})

        # Without its licence, Hexaly's own refusal is licence_unavailable, never a model failure.
        with patch.dict(os.environ, {"DCP_LICENCE_HEXALY": "none"}):
            check("licence_missing", GOOD, expected={"licence_unavailable"})

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
