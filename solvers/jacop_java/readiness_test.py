"""Readiness checks for the jacop_java integration and its current image.

Drives the repository evaluator against real containers, prints a JSON object
mapping check name to Boolean on stdout, and exits nonzero if any check failed.
`python -m generation.readiness check --solver jacop_java` runs this and keeps
its output as the readiness evidence.

A submission is one Java file declaring `class Submission` with
`static Model build(JSONObject instance, Store store)`, compiled in the image
against JaCoP, org.json and the harness jar, so this integration also has to
prove that a submission which does not compile is reported as
`compilation_error`. Every check below pays a real `javac` invocation.

What some checks actually assert. `malformed_output` returns a model that
declares no outputs, which the harness must refuse rather than emit `{}` as a
solution. `stdout_is_log` prints on `System.out` during `build`: the harness
points that stream at stderr, so the run must still be accepted.
`timeout_cleanup` uses an unsatisfiable pigeonhole rather than a sleep, so it
exercises the path where JaCoP itself is still searching when the budget runs
out. `minimization` and `maximization` ask for three solutions, so they also
check that the objective stays fixed at the optimum while enumerating: JaCoP
loses a constraint imposed between searches unless it is propagated at the
base level first, and these checks caught exactly that. `enumeration` asks for more solutions than exist, so it passes only if
the harness blocks on the declared outputs and reports exhaustion.
`partial_search` labels only one variable through `Model.search`; the harness
must still label the rest, or `y` would be emitted unfixed. `native_api`
checks that the store a submission is handed is JaCoP's own.
"""
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from evaluation import evaluate
from evaluation.execution import image_identity
from evaluation.results import EvaluationError

SOLVER = "jacop_java"

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
solution = {"x": int(x.value()), "y": int(y.value())}
print(json.dumps(solution))
'''
OPTIMIZING = REFERENCE.replace("optimize = False", "optimize = True")
MAXIMIZING = OPTIMIZING.replace("model.minimize", "model.maximize")

HEAD = ("import org.jacop.core.*;\n"
        "import org.jacop.constraints.*;\n"
        "import org.jacop.search.*;\n"
        "import org.json.JSONObject;\n"
        "import dcp.jacop.Model;\n\n"
        "public class Submission {\n"
        "    public static Model build(JSONObject inst, Store store) {\n"
        "        int n = inst.getInt(\"n\");\n"
        "        IntVar x = new IntVar(store, \"x\", 0, n);\n"
        "        IntVar y = new IntVar(store, \"y\", 0, n);\n")
TAIL = "    }\n}\n"
EXPORT = "        Model m = new Model().put(\"x\", x).put(\"y\", y);\n"

GOOD = (HEAD + "        store.impose(new XplusYeqC(x, y, n));\n"
        + EXPORT + "        return m;\n" + TAIL)
# `n` is a lower bound here, so the objective has room to move both ways.
OPTIMAL = (HEAD + "        store.impose(new XplusYgtC(x, y, n - 1));\n"
           + "        IntVar total = new IntVar(store, \"total\", 0, 2 * n);\n"
           + "        store.impose(new XplusYeqZ(x, y, total));\n"
           + EXPORT + "        return m.DIRECTION(total);\n" + TAIL)
MALFORMED = (HEAD + "        store.impose(new XplusYeqC(x, y, n));\n"
             + "        return new Model();\n" + TAIL)
NOISY = (HEAD + "        System.out.println(\"this is not a protocol record\");\n"
         + "        store.impose(new XplusYeqC(x, y, n));\n"
         + EXPORT + "        return m;\n" + TAIL)
UNSATISFIABLE = (HEAD + "        store.impose(new XeqC(x, 0));\n"
                 + "        store.impose(new XeqC(x, 1));\n"
                 + EXPORT + "        return m;\n" + TAIL)
# 40 pigeons into 39 holes with pairwise disequalities: no propagation proves
# it, so a two-second budget expires inside JaCoP's search.
SLOW = (HEAD + "        store.impose(new XplusYeqC(x, y, n));\n"
        + "        IntVar[] birds = new IntVar[40];\n"
        + "        for (int i = 0; i < 40; i++) birds[i] = new IntVar(store, 0, 38);\n"
        + "        for (int i = 0; i < 40; i++)\n"
        + "            for (int j = i + 1; j < 40; j++) store.impose(new XneqY(birds[i], birds[j]));\n"
        + EXPORT + "        return m;\n" + TAIL)
UNCOMPILABLE = "this is not Java\n"
PARTIAL = (HEAD + "        store.impose(new XplusYeqC(x, y, n));\n"
           + EXPORT
           + "        return m.search(new IntVar[]{x}, null, new IndomainMax<IntVar>());\n" + TAIL)

# Java can inspect its own container, so this check runs through the real
# submission path. A failed probe throws, which the harness reports as an
# error, so the check only passes when every probe held.
ISOLATED = '''import java.net.InetSocketAddress;
import java.net.Socket;
import java.nio.file.*;
import java.util.*;
import org.jacop.core.*;
import org.jacop.constraints.*;
import org.json.JSONObject;
import dcp.jacop.Model;

public class Submission {
    static void require(boolean ok, String what) {
        if (!ok) throw new IllegalStateException(what);
    }

    public static Model build(JSONObject inst, Store store) throws Exception {
        String status = Files.readString(Path.of("/proc/self/status"));
        String uid = status.lines().filter(l -> l.startsWith("Uid:")).findFirst().orElseThrow()
            .trim().split("\\\\s+")[1];
        require(!uid.equals("0"), "container runs as root");
        require(!Files.exists(Path.of("/dataset")), "dataset is visible to the candidate");
        Set<String> entries = new TreeSet<>();
        try (var listing = Files.list(Path.of("/input"))) {
            listing.forEach(p -> entries.add(p.getFileName().toString()));
        }
        require(entries.equals(new TreeSet<>(List.of("model.java", "request.json"))), "unexpected /input " + entries);
        boolean writable;
        try {
            Files.writeString(Path.of("/input/written"), "x");
            writable = true;
        } catch (Exception error) {
            writable = false;
        }
        require(!writable, "input is writable");
        boolean reachable;
        try (Socket socket = new Socket()) {
            socket.connect(new InetSocketAddress("1.1.1.1", 443), 500);
            reachable = true;
        } catch (Exception error) {
            reachable = false;
        }
        require(!reachable, "network reachable");

        int n = inst.getInt("n");
        IntVar x = new IntVar(store, "x", 0, n);
        IntVar y = new IntVar(store, "y", 0, n);
        store.impose(new XplusYeqC(x, y, n));
        return new Model().put("x", x).put("y", y);
    }
}
'''

# The harness must hand over JaCoP's own Store and wrap none of its API:
# constraints here are JaCoP global and decomposed constraints.
NATIVE = (HEAD
          + "        org.jacop.core.Store own = store;\n"
          + "        own.impose(new LinearInt(new IntVar[]{x, y}, new int[]{1, 1}, \"==\", n));\n"
          + "        IntVar[] spare = new IntVar[3];\n"
          + "        for (int i = 0; i < 3; i++) spare[i] = new IntVar(own, 1, 3);\n"
          + "        own.impose(new Alldifferent(spare));\n"
          + "        BooleanVar flag = new BooleanVar(own);\n"
          + "        own.impose(new Reified(new XeqC(x, 0), flag));\n"
          + EXPORT + "        return m;\n" + TAIL)

# --- readiness level 2: the bug classes tiny x + y models never reach ---
FOOT = "    }\n}\n"
IMPORTS = ("import org.jacop.core.*;\nimport org.jacop.constraints.*;\nimport org.jacop.search.*;\n"
           "import org.json.*;\nimport dcp.jacop.Model;\n\n")
CLS = "public class Submission {\n    public static Model build(JSONObject inst, Store store) {\n"


def ref(data, body):
    return f"\n# Data\n{data}\n# End of data\nimport cpmpy as cp\nimport json\n{body}\nprint(json.dumps(solution))\n"


# output_shapes: three levels, a Boolean matrix, a value beyond 32 bits.
SHAPES_REF = ref("n = 2", '''cube = cp.intvar(0, 10, shape=(2, 2, 2), name="cube")
grid = cp.boolvar(shape=(2, 2), name="grid")
big = cp.intvar(0, 40000000000, name="big")
model = cp.Model([cube[i, j, k] == i + j + k + n for i in range(2) for j in range(2) for k in range(2)],
                 [grid[i, j] == (i == j) for i in range(2) for j in range(2)],
                 big == 30000000000 + n)
model.solve()
solution = {"cube": cube.value().tolist(), "grid": grid.value().tolist(), "big": int(big.value())}''')
SHAPES = (IMPORTS + CLS + '''        int n = inst.getInt("n");
        IntVar[][][] cube = new IntVar[2][2][2];
        for (int i = 0; i < 2; i++) for (int j = 0; j < 2; j++) for (int k = 0; k < 2; k++) {
            cube[i][j][k] = new IntVar(store, 0, 10);
            store.impose(new XeqC(cube[i][j][k], i + j + k + n));
        }
        BooleanVar[][] grid = new BooleanVar[2][2];
        for (int i = 0; i < 2; i++) for (int j = 0; j < 2; j++) {
            grid[i][j] = new BooleanVar(store);
            store.impose(new XeqC(grid[i][j], i == j ? 1 : 0));
        }
        IntVar[] digits = new IntVar[11];
        for (int i = 0; i < 11; i++) digits[i] = new IntVar(store, 0, 9);
        store.impose(new XeqC(digits[0], 3));
        for (int i = 1; i < 10; i++) store.impose(new XeqC(digits[i], 0));
        store.impose(new XeqC(digits[10], n));
        return new Model().put("cube", cube).put("grid", grid).putDigits("big", digits, 10);
''' + FOOT)

# instance_shapes: ragged rows, mixed-type rows, an unused string, name/note, two shapes.
SHAPED_REF = ref('n = 2\nrows = [[1], [2, 3]]\nmixed = [[1, "a"], [2, "b"]]\nlabel = "first"',
                 '''total = cp.intvar(0, 1000, name="total")
key = cp.intvar(0, 1000, name="key")
model = cp.Model(total == n + sum(sum(row) for row in rows), key == sum(row[0] for row in mixed))
model.solve()
solution = {"total": int(total.value()), "key": int(key.value())}''')
SHAPED_INSTANCE = {"n": 3, "rows": [[4, 5, 6], [], [1]], "mixed": [[3, "c"]], "label": "second",
                   "name": "readiness", "note": "ragged rows, mixed rows, an unused string"}
SHAPED = (IMPORTS + CLS + '''        int total = inst.getInt("n");
        JSONArray rows = inst.getJSONArray("rows");
        for (int i = 0; i < rows.length(); i++) {
            JSONArray row = rows.getJSONArray(i);
            for (int j = 0; j < row.length(); j++) total += row.getInt(j);
        }
        int key = 0;
        JSONArray mixed = inst.getJSONArray("mixed");
        for (int i = 0; i < mixed.length(); i++) key += mixed.getJSONArray(i).getInt(0);
        IntVar t = new IntVar(store, "t", 0, 1000);
        IntVar k = new IntVar(store, "k", 0, 1000);
        store.impose(new XeqC(t, total));
        store.impose(new XeqC(k, key));
        return new Model().put("total", t).put("key", k);
''' + FOOT)

# error_detail: JaCoP throws FailException for an empty domain; that must come back in the detail.
FAILING = IMPORTS + CLS + '        IntVar bad = new IntVar(store, "bad", 3, 1);\n        return new Model().put("x", bad);\n' + FOOT
# A heap the size of the container: the JVM's own OutOfMemoryError must be reported.
HOG = (HEAD + "        store.impose(new XplusYeqC(x, y, n));\n"
       "        java.util.List<long[]> hog = new java.util.ArrayList<>();\n"
       "        while (true) hog.add(new long[10_000_000]);\n    }\n}\n")
# stray_stdout: the model prints on System.out; NOISY covers it.
CHATTY = NOISY

# optimum_enumeration: a sum objective with ten optima.
SUM_REF = ref("n = 2", '''x = cp.intvar(0, 2, shape=4, name="x")
model = cp.Model(cp.sum(x) >= n)
model.minimize(cp.sum(x))
model.solve()
solution = {"x": x.value().tolist()}''')
SUM = (IMPORTS + CLS + '''        int n = inst.getInt("n");
        IntVar[] x = new IntVar[4];
        for (int i = 0; i < 4; i++) x[i] = new IntVar(store, "x" + i, 0, 2);
        IntVar total = new IntVar(store, "total", 0, 8);
        store.impose(new SumInt(store, x, "==", total));
        store.impose(new XgteqC(total, n));
        return new Model().put("x", x).minimize(total);
''' + FOOT)

# minimization_step_one: the first solution found is optimum + 1 (x = 0 gives 10; the optimum 9 is at x = 1).
STEP_REF = ref("n = 2", '''x = cp.intvar(0, 10, name="x")
model = cp.Model(x <= n - 1)
model.minimize(10 - x)
model.solve()
solution = {"x": int(x.value())}''')
STEP = (IMPORTS + CLS + '''        int n = inst.getInt("n");
        IntVar x = new IntVar(store, "x", 0, 10);
        IntVar cost = new IntVar(store, "cost", 0, 10);
        store.impose(new XlteqC(x, n - 1));
        store.impose(new XplusYeqC(x, cost, 10));
        return new Model().put("x", x).minimize(cost).search(new IntVar[]{x}, null, new IndomainMin<IntVar>());
''' + FOOT)

# optimization_timeout: easy reference, but the submission adds a Golomb ruler (11 marks) to its
# objective, so a solution comes fast and the proof does not within 3 s.
EASY_MIN = ref("n = 2", '''x = cp.intvar(0, 10, name="x")
model = cp.Model(x >= n)
model.minimize(x)
model.solve()
solution = {"x": int(x.value())}''')
UNPROVABLE = (IMPORTS + CLS + '''        int n = inst.getInt("n");
        IntVar x = new IntVar(store, "x", 0, 10);
        store.impose(new XgteqC(x, n));
        IntVar[] marks = new IntVar[11];
        for (int i = 0; i < 11; i++) marks[i] = new IntVar(store, "m" + i, 0, 200);
        store.impose(new XeqC(marks[0], 0));
        for (int i = 0; i < 10; i++) store.impose(new XltY(marks[i], marks[i + 1]));
        IntVar[] diffs = new IntVar[55];
        int k = 0;
        for (int i = 0; i < 11; i++)
            for (int j = i + 1; j < 11; j++) {
                diffs[k] = new IntVar(store, "d" + k, 0, 200);
                store.impose(new XplusYeqZ(marks[i], diffs[k], marks[j]));
                k++;
            }
        store.impose(new Alldiff(diffs));
        IntVar cost = new IntVar(store, "cost", 0, 10000 + 200);
        store.impose(new LinearInt(store, new IntVar[]{x, marks[10], cost}, new int[]{1000, 1, -1}, "==", 0));
        return new Model().put("x", x).minimize(cost);
''' + FOOT)

# auxiliary_free_distinct: a free variable outside the outputs repeats each (x, y) six times.
AUXILIARY = (HEAD + "        store.impose(new XplusYeqC(x, y, n));\n"
             + '        IntVar unused = new IntVar(store, "unused", 0, 5);\n' + EXPORT + "        return m;\n" + TAIL)

# large_model: 3000 Booleans in one sum, reported as an output.
LARGE_REF = ref("n = 1500", '''b = cp.boolvar(shape=3000, name="b")
count = cp.intvar(0, 3000, name="count")
model = cp.Model(count == cp.sum(b), count == n)
model.solve()
solution = {"b": b.value().tolist(), "count": int(count.value())}''')
LARGE = (IMPORTS + CLS + '''        int n = inst.getInt("n");
        BooleanVar[] b = new BooleanVar[3000];
        for (int i = 0; i < 3000; i++) b[i] = new BooleanVar(store, "b" + i);
        IntVar count = new IntVar(store, "count", 0, 3000);
        store.impose(new SumBool(store, b, "==", count));
        store.impose(new XeqC(count, n));
        return new Model().put("b", b).put("count", count);
''' + FOOT)


def main():
    results = {}
    with tempfile.TemporaryDirectory(prefix="dcp_readiness_") as directory:
        temp = Path(directory)

        def candidate(name, source):
            path = temp / f"{name}.java"
            path.write_text(source, encoding="utf-8")
            return path

        def check(name, source, reference=REFERENCE, expected=None, detail=None, **kwargs):
            result = evaluate(candidate(name, source), "readiness", SOLVER,
                              reference_source=reference, **kwargs)
            results[name] = result["accepted"] if expected is None else (
                not result["accepted"] and result["reason"] in expected)
            if results[name] and detail is not None:
                results[name] = detail in json.dumps(result)
            if not results[name]:
                print(f"{name}: {json.dumps(result)[:1500]}", file=sys.stderr)
            return result

        check("satisfaction", GOOD)
        check("changed_instances", GOOD, instances=[{"n": 3, "optimize": False}], instance_count=2)
        enumerated = check("enumeration", GOOD, solution_limit=5)
        # Three solutions exist; anything else means duplicates or a missed one.
        counts = [item.get("solutions_checked") for item in enumerated.get("instances", [])]
        results["enumeration"] = results["enumeration"] and counts == [3]
        if counts != [3]:
            print(f"enumeration: solutions checked per instance {counts}, expected [3]", file=sys.stderr)
        check("minimization", OPTIMAL.replace("DIRECTION", "minimize"), reference=OPTIMIZING, solution_limit=3)
        check("maximization", OPTIMAL.replace("DIRECTION", "maximize"), reference=MAXIMIZING, solution_limit=3)
        check("native_api", NATIVE)
        check("stdout_is_log", NOISY)
        check("partial_search", PARTIAL, solution_limit=5)
        check("isolation", ISOLATED)
        check("malformed_output", MALFORMED, expected={"execution_error", "invalid_output"})
        check("empty_output", UNSATISFIABLE, expected={"no_solution"})
        check("timeout_cleanup", SLOW, expected={"execution_timeout"}, execution_timeout=2)
        check("compilation_error", UNCOMPILABLE, expected={"compilation_error"})
        check("out_of_memory", HOG, expected={"execution_error"}, detail="OutOfMemoryError")

        # Bug-class checks (readiness level 2).
        result = evaluate(candidate("optimization_timeout", UNPROVABLE), "readiness", SOLVER,
                          reference_source=EASY_MIN, execution_timeout=3)
        results["optimization_timeout"] = (result["reason"] == "execution_timeout"
                                           and all(item.get("solutions_received", 0) == 0
                                                   for item in result["instances"]))
        if not results["optimization_timeout"]:
            print("optimization_timeout:", json.dumps(result)[:1500], file=sys.stderr)
        check("minimization_step_one", STEP, reference=STEP_REF)
        result = check("optimum_enumeration", SUM, reference=SUM_REF, solution_limit=3)
        results["optimum_enumeration"] = results["optimum_enumeration"] and result["solutions_checked"] == 3
        check("output_shapes", SHAPES, reference=SHAPES_REF)
        check("instance_shapes", SHAPED, reference=SHAPED_REF, instances=[SHAPED_INSTANCE], instance_count=2)
        check("error_detail", FAILING, expected={"execution_error"}, detail="FailException")
        check("stray_stdout", CHATTY)
        result = check("auxiliary_free_distinct", AUXILIARY, solution_limit=3)
        results["auxiliary_free_distinct"] = results["auxiliary_free_distinct"] and result["solutions_checked"] == 3
        check("large_model", LARGE, reference=LARGE_REF, execution_timeout=120, reference_timeout=120)

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
