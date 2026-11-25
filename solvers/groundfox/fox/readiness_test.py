"""Readiness checks for the groundfox_fox integration and its current image.

Drives the repository evaluator against real containers, prints a JSON object
mapping check name to Boolean on stdout, and exits nonzero if any check failed.
`python -m generation.readiness check --solver groundfox_fox` runs this and keeps
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

SOLVER = "groundfox_fox"

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

def fox(vocab_in, vocab_out, theory, body="    return {}\n", flags=None, pre=""):
    text = (pre + 'FOX = """\ninvocabulary { %s }\noutvocabulary { %s }\ntheory {\n%s\n}\n"""\n'
            % (vocab_in, vocab_out, theory))
    if flags is not None:
        text += "FLAGS = %r\n" % (flags,)
    return text + "\ndef structure(instance):\n" + body


XY_THEORY = """    ? a [Val(a)] : x(a).
    ! a [Val(a)] : ! b [Val(b) & ~(a = b)] : ~x(a) | ~x(b).
    ? a [Val(a)] : y(a).
    ! a [Val(a)] : ! b [Val(b) & ~(a = b)] : ~y(a) | ~y(b).
    ! a : ! b [Val(a) & Val(b) & ~Sum(a, b)] : ~x(a) | ~y(b).
"""
XY_BODY = ("    n = instance['n']\n"
           "    return {'Val': range(n + 1),\n"
           "            'Sum': [(a, b) for a in range(n + 1) for b in range(n + 1) if a + b == n]}\n")


def xy(body=XY_BODY, theory=XY_THEORY, pre=""):
    return fox("Val/1 Sum/2", "x/1 y/1", theory, body, pre=pre)


GOOD = xy()
# unsupported_optimization: this integration takes no objective, so a satisfaction model of
# an optimisation problem must be rejected when its answer is not optimal (x + y is n + 1,
# the optimum n). FOX has no objective syntax to refuse.
NOT_OPTIMAL = xy(body=XY_BODY.replace("a + b == n", "a + b == n + 1").replace(
    "range(n + 1) for b", "range(n + 2) for b").replace("'Val': range(n + 1)", "'Val': range(n + 2)"))
MALFORMED = "def structure(instance):\n    return {}\n"
UNSATISFIABLE = fox("Val/1", "x/1 y/1", "    ? a [Val(a)] : x(a).\n    ! a [Val(a)] : ~x(a).\n",
                    "    return {'Val': [0, 1]}\n")
SLOW = xy(body="    import time\n    time.sleep(120)\n" + XY_BODY)
ISOLATED = xy(body=("    import os, socket\n"
                    "    def host_uid(uid):\n"
                    "        for line in open('/proc/self/uid_map'):\n"
                    "            inside, outside, count = map(int, line.split())\n"
                    "            if inside <= uid < inside + count:\n"
                    "                return outside + uid - inside\n"
                    "    assert os.getuid() != 0 or host_uid(0) != 0, 'container has host root privilege'\n"
                    "    assert sorted(os.listdir('/input')) == ['model.py', 'request.json'], 'unexpected /input'\n"
                    "    assert not os.path.exists('/dataset'), 'dataset is visible to the candidate'\n"
                    "    probe = socket.socket()\n"
                    "    probe.settimeout(0.5)\n"
                    "    assert probe.connect_ex(('1.1.1.1', 443)) != 0, 'network reachable'\n") + XY_BODY)

# Bug-class checks (readiness_level 2). Each one is accepted only when the runner
# does what the contract says; see CONTRACT.md.
NESTED_REFERENCE = '''
import cpmpy as cp
import json
x = cp.intvar(0, 2, name="x")
y = cp.intvar(0, 2, name="y")
model = cp.Model(x + y == 2)
model.solve()
solution = {"m": [[[int(x.value()), int(y.value())], [int(y.value()), int(x.value())]]],
            "v": [int(x.value()), int(y.value())]}
print(json.dumps(solution))
'''
# m is a three-level array [1][2][2] fixed to x=0, y=2 by the theory
NESTED_SUBMISSION = fox("Val/1 Idx/1", "m/4 v/2", """
    ! i [Idx(i)] : ? a [Val(a)] : v(i, a).
    ! i [Idx(i)] : ! a [Val(a)] : ! b [Val(b) & ~(a = b)] : ~v(i, a) | ~v(i, b).
    ! i [Idx(i)] : ! j [Idx(j)] : ? a [Val(a)] : m(0, i, j, a).
    ! i [Idx(i)] : ! j [Idx(j)] : ! a [Val(a)] : ! b [Val(b) & ~(a = b)] : ~m(0, i, j, a) | ~m(0, i, j, b).
    ! u [u = 0] : v(0, 0). ! u [u = 0] : v(1, 2).
    ! u [u = 0] : m(0, 0, 0, 0). ! u [u = 0] : m(0, 0, 1, 2). ! u [u = 0] : m(0, 1, 0, 2). ! u [u = 0] : m(0, 1, 1, 0).
""", "    return {'Val': range(3), 'Idx': range(2)}\n")
BOOL_REFERENCE = '''
import cpmpy as cp
import json
x = cp.intvar(0, 2, name="x")
model = cp.Model(x >= 1)
model.solve()
solution = {"x": int(x.value()), "b": [[True, False], [False, True]], "big": 5000000000}
print(json.dumps(solution))
'''
# A Boolean matrix (0/1 values), an integer and a value beyond 32 bits.
BOOL_SUBMISSION = fox("Val/1 Bit/1 Big/1", "x/1 b/3 big/1", """
    ? a [Val(a)] : x(a).
    ! a [Val(a)] : ! c [Val(c) & ~(a = c)] : ~x(a) | ~x(c).
    ! u [u = 0] : ~x(0).
    ! i [Bit(i)] : ! j [Bit(j)] : ? v [Bit(v)] : b(i, j, v).
    ! i [Bit(i)] : ! j [Bit(j)] : ! v [Bit(v)] : ! w [Bit(w) & ~(v = w)] : ~b(i, j, v) | ~b(i, j, w).
    ! u [u = 0] : b(0, 0, 1). ! u [u = 0] : b(0, 1, 0). ! u [u = 0] : b(1, 0, 0). ! u [u = 0] : b(1, 1, 1).
    ? v [Big(v)] : big(v).
    ! v [Big(v)] : ! w [Big(w) & ~(v = w)] : ~big(v) | ~big(w).
""", "    return {'Val': range(3), 'Bit': [0, 1], 'Big': [5000000000]}\n")
# error_detail: a sentence not in GNF makes groundfox itself fail.
ERROR_SUBMISSION = fox("Val/1", "x/1", "    ? a [Val(a)] : x(a).\n    ! a [Val(a)] : x(a) => x(a).\n",
                       "    return {'Val': [0, 1]}\n")
STDOUT_SUBMISSION = xy(body="    print('more noise')\n" + XY_BODY, pre="print('model noise on stdout')\n")
# A free auxiliary predicate outside the outputs: distinct solutions only.
AUX_SUBMISSION = fox("Val/1 Sum/2", "x/1 y/1 aux/1", XY_THEORY + "    ! a [Val(a)] : aux(a) | ~aux(a).\n", XY_BODY)
LARGE_REFERENCE = '''
import cpmpy as cp
import json
bs = cp.boolvar(shape=3000, name="b")
model = cp.Model(cp.sum(bs) == 3000)
model.solve()
solution = {"b": [1] * 3000}
print(json.dumps(solution))
'''
LARGE_SUBMISSION = fox("Idx/1 Bit/1", "b/2", """
    ! i [Idx(i)] : ? v [Bit(v)] : b(i, v).
    ! i [Idx(i)] : ! v [Bit(v)] : ! w [Bit(w) & ~(v = w)] : ~b(i, v) | ~b(i, w).
    ! i [Idx(i)] : b(i, 1).
""", "    return {'Idx': range(3000), 'Bit': [0, 1]}\n")
# Pigeonhole: 15 pigeons, 14 holes, hard for the SAT solver.
PIGEONHOLE = fox("Pigeon/1 Hole/1 Val/1", "p/2 x/1 y/1", """
    ! u [u = 0] : x(0). ! u [u = 0] : y(0).
    ! i [Pigeon(i)] : ? h [Hole(h)] : p(i, h).
    ! i [Pigeon(i)] : ! j [Pigeon(j) & ~(i = j)] : ! h [Hole(h)] : ~p(i, h) | ~p(j, h).
""", "    return {'Pigeon': range(15), 'Hole': range(14), 'Val': [0]}\n")

# standalone_block: a run block at the end that would fail if the runner executed it
# (it reads a file named on the command line).
STANDALONE = GOOD + (
    "\n\nif __name__ == '__main__':\n"
    "    import json\n"
    "    import sys\n"
    "    instances = json.load(open(sys.argv[1]))\n"
    "    print(structure(instances[0]))\n")


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
                          "ragged": [[1], [2, 3]], "mixed": [[1, "a"], [True, 2.5]]},
                         {"n": 3, "optimize": False, "name": "c", "note": "d", "label": "t",
                          "ragged": [[4, 5, 6]], "mixed": [["z"], [None]]}],
              instance_count=2)
        check("enumeration", GOOD, solution_limit=3)
        check("unsupported_optimization", NOT_OPTIMAL, reference=OPTIMIZING,
              expected={"suboptimal_solution", "invalid_solution", "wrong_solution"})
        check("isolation", ISOLATED)
        check("malformed_output", MALFORMED, expected={"execution_error", "invalid_output"})
        check("empty_output", UNSATISFIABLE, expected={"no_solution"})
        check("timeout_cleanup", SLOW, expected={"execution_timeout"}, execution_timeout=2)
        check("standalone_block", STANDALONE)

        # timeout_classification: a hard unsat-free instance still times out, never errors
        check("timeout_classification", PIGEONHOLE, expected={"execution_timeout"},
              execution_timeout=2, reference=REFERENCE)
        check("output_shapes", NESTED_SUBMISSION, reference=NESTED_REFERENCE)
        check("bool_leaves", BOOL_SUBMISSION, reference=BOOL_REFERENCE)
        check("auxiliary_free_distinct", AUX_SUBMISSION, solution_limit=3)
        check("stray_stdout", STDOUT_SUBMISSION, reference=REFERENCE)
        check("large_model", LARGE_SUBMISSION, reference=LARGE_REFERENCE, execution_timeout=120)
        error = check("error_detail", ERROR_SUBMISSION, expected={"execution_error"})
        results["error_detail"] = (not error["accepted"] and error["reason"] == "execution_error"
                                   and "groundfox" in json.dumps(error))

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
