"""Readiness checks for the yices_python integration and its current image.

Drives the repository evaluator against real containers, prints a JSON object
mapping check name to Boolean on stdout, and exits nonzero if any check failed.
`python -m generation.readiness check --solver yices_python` runs this and keeps
its output as the readiness evidence.
"""
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from evaluation import evaluate
from evaluation.execution import image_identity
from evaluation.results import EvaluationError

SOLVER = "yices_python"

# Trusted references, kept here so this script does not depend on the test
# suite. n=2 gives x+y==2 exactly three solutions.
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
solution = {"x": int(x.value()), "y": int(y.value())}
print(json.dumps(solution))
'''
OPTIMIZING = REFERENCE.replace("optimize = False", "optimize = True")
MAXIMIZING = OPTIMIZING.replace("model.minimize", "model.maximize")

PRE = ("from yices import Terms, Types\n"
       "I = Terms.integer\n"
       "def iv(name):\n"
       "    return Terms.new_uninterpreted_term(Types.int_type(), name)\n"
       "def bv(name):\n"
       "    return Terms.new_uninterpreted_term(Types.bool_type(), name)\n"
       "def ge(a, b): return Terms.arith_geq_atom(a, b)\n"
       "def le(a, b): return Terms.arith_leq_atom(a, b)\n"
       "def eq(a, b): return Terms.arith_eq_atom(a, b)\n"
       "def box(v, lo, hi): return [ge(v, I(lo)), le(v, I(hi))]\n")


def sub(body):
    return PRE + body


GOOD = sub("def build(instance):\n"
           "    n = instance['n']\n"
           "    x, y = iv('x'), iv('y')\n"
           "    f = box(x, 0, n) + box(y, 0, n) + [eq(Terms.add(x, y), I(n))]\n"
           "    return f, {'x': x, 'y': y}\n")
OPTIMAL = sub("def build(instance):\n"
              "    n = instance['n']\n"
              "    x, y = iv('x'), iv('y')\n"
              "    f = box(x, 0, n) + box(y, 0, n) + [ge(Terms.add(x, y), I(n))]\n"
              "    return f, {'x': x, 'y': y}, ('DIRECTION', Terms.add(x, y))\n")
MALFORMED = "def build(instance):\n    return None, {}\n"
UNSATISFIABLE = sub("def build(instance):\n"
                    "    x = iv('x')\n"
                    "    return [Terms.false()], {'x': x, 'y': I(2)}\n")
SLOW = "import time\ndef build(instance):\n    time.sleep(120)\n"
ISOLATED = ("import os, socket\n" + PRE +
            "def build(instance):\n"
            "    assert os.getuid() != 0, 'container runs as root'\n"
            "    assert sorted(os.listdir('/input')) == ['model.py', 'request.json'], 'unexpected /input'\n"
            "    assert not os.path.exists('/dataset'), 'dataset is visible to the candidate'\n"
            "    probe = socket.socket()\n"
            "    probe.settimeout(0.5)\n"
            "    assert probe.connect_ex(('1.1.1.1', 443)) != 0, 'network reachable'\n"
            "    n = instance['n']\n"
            "    x, y = iv('x'), iv('y')\n"
            "    f = box(x, 0, n) + box(y, 0, n) + [eq(Terms.add(x, y), I(n))]\n"
            "    return f, {'x': x, 'y': y}\n")

# Bug-class checks (readiness_level 2). Each one is accepted only when the runner
# does what the contract says; see CONTRACT.md.
NEGATIVE_REFERENCE = '''
import cpmpy as cp
import json
x = cp.intvar(0, 2, name="x")
y = cp.intvar(0, 2, name="y")
model = cp.Model(x + y >= 1)
model.DIRECTION(-2 * x - y + 5)
model.solve()
solution = {"x": int(x.value()), "y": int(y.value())}
print(json.dumps(solution))
'''
NEGATIVE_SUBMISSION = sub("def build(instance):\n"
                          "    x, y = iv('x'), iv('y')\n"
                          "    f = box(x, 0, 2) + box(y, 0, 2) + [ge(Terms.add(x, y), I(1))]\n"
                          "    obj = Terms.add(Terms.add(Terms.mul(I(-2), x), Terms.mul(I(-1), y)), I(5))\n"
                          "    return f, {'x': x, 'y': y}, ('DIRECTION', obj)\n")
# The first model Yices finds for this problem is not the optimum (checked by hand in
# the image); the optimum is 8 at (0, 4). The runner must tighten the objective to prove it.
PROOF_REFERENCE = '''
import cpmpy as cp
import json
x = cp.intvar(0, 9, name="x")
y = cp.intvar(0, 9, name="y")
model = cp.Model(x + 2 * y >= 7)
model.minimize(3 * x + 2 * y)
model.solve()
solution = {"x": int(x.value()), "y": int(y.value())}
print(json.dumps(solution))
'''
PROOF_SUBMISSION = sub("def build(instance):\n"
                       "    x, y = iv('x'), iv('y')\n"
                       "    f = box(x, 0, 9) + box(y, 0, 9)\n"
                       "    f += [ge(Terms.add(x, Terms.mul(I(2), y)), I(7))]\n"
                       "    obj = Terms.add(Terms.mul(I(3), x), Terms.mul(I(2), y))\n"
                       "    return f, {'x': x, 'y': y}, ('minimize', obj)\n")
# Ten optima (x+y==4 over five pairs, times two values of z), solution_limit 3.
OPTIMA_REFERENCE = '''
import cpmpy as cp
import json
x = cp.intvar(0, 4, name="x")
y = cp.intvar(0, 4, name="y")
z = cp.intvar(0, 1, name="z")
model = cp.Model(x + y == 4)
model.minimize(x + y)
model.solve()
solution = {"x": int(x.value()), "y": int(y.value()), "z": int(z.value())}
print(json.dumps(solution))
'''
OPTIMA_SUBMISSION = sub("def build(instance):\n"
                        "    x, y, z = iv('x'), iv('y'), iv('z')\n"
                        "    f = box(x, 0, 4) + box(y, 0, 4) + box(z, 0, 1) + [eq(Terms.add(x, y), I(4))]\n"
                        "    return f, {'x': x, 'y': y, 'z': z}, ('minimize', Terms.add(x, y))\n")
NESTED_REFERENCE = '''
import cpmpy as cp
import json
x = cp.intvar(0, 2, name="x")
y = cp.intvar(0, 2, name="y")
model = cp.Model(x + y == 2)
model.solve()
solution = {"m": [[[int(x.value())], [int(y.value())]], [[int(y.value())], [int(x.value())]]],
            "v": [int(x.value()), int(y.value())], "w": 2 ** 40 + int(x.value())}
print(json.dumps(solution))
'''
NESTED_SUBMISSION = sub("def build(instance):\n"
                        "    x, y = iv('x'), iv('y')\n"
                        "    f = box(x, 0, 2) + box(y, 0, 2) + [eq(Terms.add(x, y), I(2))]\n"
                        "    w = Terms.add(x, I(2 ** 40))\n"
                        "    return f, {'m': [[[x], [y]], [[y], [x]]], 'v': [x, y], 'w': w}\n")
BOOL_REFERENCE = '''
import cpmpy as cp
import json
x = cp.intvar(0, 2, name="x")
model = cp.Model(x >= 1)
model.solve()
solution = {"x": int(x.value()), "b": bool(x.value() >= 1), "c": True}
print(json.dumps(solution))
'''
BOOL_SUBMISSION = sub("def build(instance):\n"
                      "    x, b = iv('x'), bv('b')\n"
                      "    f = box(x, 1, 2) + [Terms.eq(b, ge(x, I(1)))]\n"
                      "    return f, {'x': x, 'b': b, 'c': True}\n")
ERROR_SUBMISSION = sub("def build(instance):\n"
                       "    x, y = iv('x'), iv('y')\n"
                       "    f = box(x, 0, 3) + box(y, 0, 3) + [eq(Terms.mul(x, y), I(2))]\n"
                       "    return f, {'x': x, 'y': y}\n")
STDOUT_SUBMISSION = ("print('model noise on stdout')\n" + GOOD.replace(
    "    return f,", "    print('more noise')\n    Terms.print_to_fd(1, f[0], 80, 1, 0)\n    return f,"))
AUX_SUBMISSION = sub("def build(instance):\n"
                     "    x, y, a = iv('x'), iv('y'), iv('a')\n"
                     "    f = box(x, 0, 2) + box(y, 0, 2) + box(a, 0, 2) + [eq(Terms.add(x, y), I(2))]\n"
                     "    return f, {'x': x, 'y': y}\n")
LARGE_REFERENCE = '''
import cpmpy as cp
import json
bs = cp.boolvar(shape=3000, name="b")
model = cp.Model(cp.sum(bs) == 1500)
model.solve()
solution = {"total": 1500}
print(json.dumps(solution))
'''
LARGE_SUBMISSION = sub("def build(instance):\n"
                       "    bs = [bv('b%d' % i) for i in range(3000)]\n"
                       "    total = Terms.sum([Terms.ite(b, I(1), I(0)) for b in bs])\n"
                       "    return [eq(total, I(1500))], {'total': total}\n")
# Golomb ruler on 10 marks with an easy reference: the submission's objective
# includes the ruler length, whose optimality is far too hard for 3 s.
TIMEOUT_SUBMISSION = sub("def build(instance):\n"
                         "    x, y = iv('x'), iv('y')\n"
                         "    marks = [iv('m%d' % i) for i in range(10)]\n"
                         "    f = box(x, 0, 2) + box(y, 0, 2) + [ge(Terms.add(x, y), I(1))]\n"
                         "    f += [eq(marks[0], I(0))]\n"
                         "    f += [Terms.arith_lt_atom(marks[i], marks[i + 1]) for i in range(9)]\n"
                         "    f += [le(m, I(60)) for m in marks]\n"
                         "    diffs = [Terms.sub(marks[j], marks[i]) for i in range(10) for j in range(i + 1, 10)]\n"
                         "    f += [Terms.distinct(diffs)]\n"
                         "    return f, {'x': x, 'y': y}, ('minimize', Terms.add(Terms.add(x, y), marks[9]))\n")
# x * y is nonlinear: the default context refuses it; LOGIC = 'QF_NIA' selects MCSAT.
NONLINEAR = sub("LOGIC = LOGIC_VALUE\n"
                "def build(instance):\n"
                "    n = instance['n']\n"
                "    x, y = iv('x'), iv('y')\n"
                "    f = box(x, 0, n) + box(y, 0, n) + [eq(Terms.add(x, y), I(n)), ge(Terms.mul(x, y), I(0))]\n"
                "    return f, {'x': x, 'y': y}\n")
# A Python comparison is a bool, not a term: the runner must say so.
PYTHON_BOOL = sub("def build(instance):\n"
                  "    x = iv('x')\n"
                  "    return box(x, 0, 2) + [x > 1], {'x': x}\n")
# 14 pigeons in 13 holes: unsat but far beyond 2 s.
PIGEONHOLE = sub("def build(instance):\n"
                 "    xs = [iv('p%d' % i) for i in range(14)]\n"
                 "    f = [c for x in xs for c in box(x, 0, 12)]\n"
                 "    f += [Terms.distinct(xs)]\n"
                 "    return f, {'p0': xs[0]}\n")


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
        # instance_shapes: extra keys, a string and ragged data are ignored by the
        # submission (it reads only `n`), on two instances of different shapes.
        check("instance_shapes", GOOD,
              instances=[{"n": 2, "optimize": False, "name": "a", "note": "b", "label": "s",
                          "ragged": [[1], [2, 3]]},
                         {"n": 3, "optimize": False, "name": "c", "note": "d", "label": "t",
                          "ragged": [[4, 5, 6]]}],
              instance_count=2)
        check("enumeration", GOOD, solution_limit=3)
        check("minimization", OPTIMAL.replace("DIRECTION", "minimize"), reference=OPTIMIZING)
        check("maximization", OPTIMAL.replace("DIRECTION", "maximize"), reference=MAXIMIZING)
        check("isolation", ISOLATED)
        check("malformed_output", MALFORMED, expected={"execution_error", "invalid_output"})
        check("empty_output", UNSATISFIABLE, expected={"no_solution"})
        check("timeout_cleanup", SLOW, expected={"execution_timeout"}, execution_timeout=2)

        # optimization_timeout: a proof that cannot finish in 3 s returns no solution
        check("optimization_timeout", TIMEOUT_SUBMISSION, expected={"execution_timeout"},
              execution_timeout=3)
        # a hard unsat instance still times out, never errors
        check("timeout_classification", PIGEONHOLE, expected={"execution_timeout"},
              execution_timeout=2, reference=REFERENCE)
        check("minimization_step_one", PROOF_SUBMISSION,
              reference=PROOF_REFERENCE, solution_limit=1)
        check("negative_offset_minimize", NEGATIVE_SUBMISSION.replace("DIRECTION", "minimize"),
              reference=NEGATIVE_REFERENCE.replace("DIRECTION", "minimize"))
        check("negative_offset_maximize", NEGATIVE_SUBMISSION.replace("DIRECTION", "maximize"),
              reference=NEGATIVE_REFERENCE.replace("DIRECTION", "maximize"))
        check("optimum_enumeration", OPTIMA_SUBMISSION, reference=OPTIMA_REFERENCE, solution_limit=3)
        check("output_shapes", NESTED_SUBMISSION, reference=NESTED_REFERENCE)
        check("bool_leaves", BOOL_SUBMISSION, reference=BOOL_REFERENCE)
        check("auxiliary_free_distinct", AUX_SUBMISSION, solution_limit=3)
        check("stray_stdout", STDOUT_SUBMISSION, reference=REFERENCE)
        check("large_model", LARGE_SUBMISSION, reference=LARGE_REFERENCE, execution_timeout=120)
        # Nonlinear arithmetic: refused by the default context, accepted under LOGIC = 'QF_NIA'.
        nonlinear = check("nonlinear_default_logic", NONLINEAR.replace("LOGIC_VALUE", "None"),
                          expected={"execution_error"})
        results["nonlinear_default_logic"] = (results["nonlinear_default_logic"]
                                              and "non-linear" in json.dumps(nonlinear))
        check("logic_honoured", NONLINEAR.replace("LOGIC_VALUE", "'QF_NIA'"), solution_limit=3)
        error = check("error_detail", ERROR_SUBMISSION, expected={"execution_error"})
        results["error_detail"] = (not error["accepted"] and error["reason"] == "execution_error"
                                   and "non-linear" in json.dumps(error))
        python_bool = check("python_bool_formula", PYTHON_BOOL, expected={"execution_error"})
        results["python_bool_formula"] = (results["python_bool_formula"]
                                          and "not a Boolean Yices term" in json.dumps(python_bool))

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
