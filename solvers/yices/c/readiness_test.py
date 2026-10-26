"""Readiness checks for the yices_c integration and its current image.

Drives the repository evaluator against real containers, prints a JSON object
mapping check name to Boolean on stdout, and exits nonzero if any check failed.
`python -m generation.readiness check --solver yices_c` runs this and keeps
its output as the readiness evidence.

Every submission is one C file that includes dcp.h and defines
build(const cJSON *instance). The image compiles it against the driver.
"""
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from evaluation import evaluate
from evaluation.execution import image_identity
from evaluation.results import EvaluationError

SOLVER = "yices_c"

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
FLAG_REFERENCE = REFERENCE.replace(
    'solution = {"x": int(x.value()), "y": int(y.value())}',
    'solution = {"x": int(x.value()), "y": int(y.value()), "flag": bool(x.value() == 0)}')
CONSTANT_REFERENCE = REFERENCE.replace(
    'solution = {"x": int(x.value()), "y": int(y.value())}',
    'solution = {"x": int(x.value()), "y": int(y.value()), "k": 5}')
NESTED_REFERENCE = REFERENCE.replace(
    'solution = {"x": int(x.value()), "y": int(y.value())}',
    'solution = {"x": int(x.value()), "y": int(y.value()), '
    '"cube": [[[int(x.value()), int(y.value())], [int(y.value()), int(x.value())]]], '
    '"flags": [[bool(x.value() == 0), bool(y.value() == 0)]], '
    '"big": 30000000000 + 10 * int(x.value()) + int(y.value())}')

OFFSET_REF = """
# Data
n = 3
# End of data
import cpmpy as cp
import json
x = cp.intvar(-n, n, name="x")
y = cp.intvar(-n, n, name="y")
model = cp.Model(x + y >= -2)
model.minimize(2 * x - 3 * y - 5)
model.solve()
solution = {"x": int(x.value()), "y": int(y.value())}
print(json.dumps(solution))
"""
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
OFFSET_MAX_REF = OFFSET_REF.replace("model.minimize(2 * x - 3 * y - 5)", "model.maximize(-x + 2 * y + 7)")
STEP_REF = EASY_MIN.replace("x >= n", "x >= n - 1")

# Helpers shared by the models below: a declared integer variable and its bounds.
PRELUDE = '''#include "dcp.h"

static term_t var(int lo, int hi) {
  term_t v = yices_new_uninterpreted_term(yices_int_type());
  dcp_assert(yices_arith_geq_atom(v, yices_int32(lo)));
  dcp_assert(yices_arith_leq_atom(v, yices_int32(hi)));
  return v;
}
'''

GOOD = PRELUDE + '''
void build(const cJSON *instance) {
  int n = (int)dcp_int(dcp_get(instance, "n"));
  term_t x = var(0, n), y = var(0, n);
  dcp_assert(yices_arith_eq_atom(yices_add(x, y), yices_int32(n)));
  dcp_output("x", dcp_term(x));
  dcp_output("y", dcp_term(y));
}
'''


def optimal(direction):
    return PRELUDE + f'''
void build(const cJSON *instance) {{
  int n = (int)dcp_int(dcp_get(instance, "n"));
  term_t x = var(0, n), y = var(0, n);
  term_t sum = yices_add(x, y);
  dcp_assert(yices_arith_geq_atom(sum, yices_int32(n)));
  dcp_{direction}(sum);
  dcp_output("x", dcp_term(x));
  dcp_output("y", dcp_term(y));
}}
'''


OPTIMAL_MIN = optimal("minimize")
OPTIMAL_MAX = optimal("maximize")
OFFSET_MIN = PRELUDE + '''
/* Minimise 2x - 3y - 5 with x + y >= -2 over -3..3: a negative offset and negative terms. */
void build(const cJSON *instance) {
  int n = (int)dcp_int(dcp_get(instance, "n"));
  term_t x = var(-n, n), y = var(-n, n);
  dcp_assert(yices_arith_geq_atom(yices_add(x, y), yices_int32(-2)));
  term_t obj = yices_sub(yices_sub(yices_mul(yices_int32(2), x), yices_mul(yices_int32(3), y)), yices_int32(5));
  dcp_minimize(obj);
  dcp_output("x", dcp_term(x));
  dcp_output("y", dcp_term(y));
}
'''
OFFSET_MAX = OFFSET_MIN.replace(
    "yices_sub(yices_sub(yices_mul(yices_int32(2), x), yices_mul(yices_int32(3), y)), yices_int32(5))",
    "yices_add(yices_add(yices_neg(x), yices_mul(yices_int32(2), y)), yices_int32(7))").replace(
    "dcp_minimize", "dcp_maximize").replace("Minimise 2x - 3y - 5", "Maximise -x + 2y + 7")
BOOL_OUTPUT = PRELUDE + '''
/* flag is true exactly when x == 0. */
void build(const cJSON *instance) {
  int n = (int)dcp_int(dcp_get(instance, "n"));
  term_t x = var(0, n), y = var(0, n);
  dcp_assert(yices_arith_eq_atom(yices_add(x, y), yices_int32(n)));
  term_t flag = yices_new_uninterpreted_term(yices_bool_type());
  dcp_assert(yices_iff(flag, yices_arith_eq_atom(x, yices_int32(0))));
  dcp_output("x", dcp_term(x));
  dcp_output("y", dcp_term(y));
  dcp_output("flag", dcp_term(flag));
}
'''
CONSTANT_OUTPUT = GOOD.replace('  dcp_output("y", dcp_term(y));\n',
                               '  dcp_output("y", dcp_term(y));\n  dcp_output("k", dcp_term(yices_int32(5)));\n')
NESTED = PRELUDE + '''
void build(const cJSON *instance) {
  int n = (int)dcp_int(dcp_get(instance, "n"));
  term_t x = var(0, n), y = var(0, n);
  dcp_assert(yices_arith_eq_atom(yices_add(x, y), yices_int32(n)));
  term_t fx = yices_new_uninterpreted_term(yices_bool_type());
  term_t fy = yices_new_uninterpreted_term(yices_bool_type());
  dcp_assert(yices_iff(fx, yices_arith_eq_atom(x, yices_int32(0))));
  dcp_assert(yices_iff(fy, yices_arith_eq_atom(y, yices_int32(0))));
  term_t pair1[2] = {x, y}, pair2[2] = {y, x};
  cJSON *cube = cJSON_CreateArray(), *plane = cJSON_CreateArray(), *flags = cJSON_CreateArray(), *row = cJSON_CreateArray();
  for (int k = 0; k < 2; k++) {
    cJSON *line = cJSON_CreateArray();
    for (int m = 0; m < 2; m++) cJSON_AddItemToArray(line, dcp_term(k ? pair2[m] : pair1[m]));
    cJSON_AddItemToArray(plane, line);
  }
  cJSON_AddItemToArray(cube, plane);
  cJSON_AddItemToArray(row, dcp_term(fx));
  cJSON_AddItemToArray(row, dcp_term(fy));
  cJSON_AddItemToArray(flags, row);
  dcp_output("x", dcp_term(x));
  dcp_output("y", dcp_term(y));
  dcp_output("cube", cube);
  dcp_output("flags", flags);
  dcp_output("big", dcp_term(yices_add(yices_int64(30000000000LL), yices_add(yices_mul(yices_int32(10), x), y))));
}
'''
SHAPED = '''#include "dcp.h"

/* Reads the ragged and mixed fields from the JSON instance; label, name and note are ignored. */
void build(const cJSON *instance) {
  long long total = dcp_int(dcp_get(instance, "n")), key = 0;
  const cJSON *row, *item;
  cJSON_ArrayForEach(row, dcp_get(instance, "rows"))
    cJSON_ArrayForEach(item, row) total += dcp_int(item);
  cJSON_ArrayForEach(row, dcp_get(instance, "mixed")) key += dcp_int(cJSON_GetArrayItem(row, 0));
  dcp_output("total", dcp_term(yices_int64(total)));
  dcp_output("key", dcp_term(yices_int64(key)));
}
'''
# error_detail: Yices itself rejects the model (a product of variables in the default logic).
FAILING = PRELUDE + '''
void build(const cJSON *instance) {
  int n = (int)dcp_int(dcp_get(instance, "n"));
  term_t x = var(0, n), y = var(0, n);
  dcp_assert(yices_arith_eq_atom(yices_mul(x, y), yices_int32(1)));
  dcp_output("x", dcp_term(x));
}
'''
# The same product is fine when the submission asks for the nonlinear logic.
NONLINEAR = PRELUDE + '''
void build(const cJSON *instance) {
  int n = (int)dcp_int(dcp_get(instance, "n"));
  dcp_set_logic("QF_NIA");
  term_t x = var(1, 20), y = var(1, 20);
  dcp_assert(yices_arith_eq_atom(yices_mul(x, y), yices_int32(6 * n)));
  dcp_assert(yices_arith_lt_atom(x, y));
  dcp_output("x", dcp_term(x));
  dcp_output("y", dcp_term(y));
}
'''
NONLINEAR_REF = """
# Data
n = 2
# End of data
import cpmpy as cp
import json
x = cp.intvar(1, 20, name="x")
y = cp.intvar(1, 20, name="y")
model = cp.Model(x * y == 6 * n, x < y)
model.solve()
solution = {"x": int(x.value()), "y": int(y.value())}
print(json.dumps(solution))
"""
# A type error in a builder: yices_add of an integer and a Boolean returns NULL_TERM.
BAD_TERM = PRELUDE + '''
void build(const cJSON *instance) {
  int n = (int)dcp_int(dcp_get(instance, "n"));
  term_t x = var(0, n);
  term_t bad = yices_add(x, yices_true());
  dcp_assert(yices_arith_geq_atom(bad, yices_int32(0)));
  dcp_output("x", dcp_term(x));
}
'''
SEGFAULT = '''#include "dcp.h"

void build(const cJSON *instance) {
  volatile int *p = 0;
  *p = 1;
}
'''
# stray_stdout: the model prints with printf and with Yices' own printer.
CHATTY = PRELUDE + '''
#include <stdio.h>
void build(const cJSON *instance) {
  printf("building the model\\n");
  int n = (int)dcp_int(dcp_get(instance, "n"));
  term_t x = var(0, n), y = var(0, n);
  yices_pp_term(stdout, yices_add(x, y), 80, 1, 0);
  fflush(stdout);
  dcp_assert(yices_arith_eq_atom(yices_add(x, y), yices_int32(n)));
  dcp_output("x", dcp_term(x));
  dcp_output("y", dcp_term(y));
}
'''
# auxiliary_free_distinct: a free auxiliary term outside the outputs must not repeat solutions.
AUXILIARY = GOOD.replace('  dcp_output("x"', '  (void)var(0, 5); /* spare, not an output */\n  dcp_output("x"')
SUM = PRELUDE + '''
/* Four values in 0..2 with a sum of at least n, minimising the sum: ten optima. */
void build(const cJSON *instance) {
  int n = (int)dcp_int(dcp_get(instance, "n"));
  term_t x[4];
  cJSON *out = cJSON_CreateArray();
  for (int i = 0; i < 4; i++) {
    x[i] = var(0, 2);
    cJSON_AddItemToArray(out, dcp_term(x[i]));
  }
  term_t total = yices_sum(4, x);
  dcp_assert(yices_arith_geq_atom(total, yices_int32(n)));
  dcp_minimize(total);
  dcp_output("x", out);
}
'''
SHAPES = PRELUDE + '''
void build(const cJSON *instance) {
  int n = (int)dcp_int(dcp_get(instance, "n"));
  cJSON *cube = cJSON_CreateArray(), *grid = cJSON_CreateArray();
  for (int i = 0; i < 2; i++) {
    cJSON *plane = cJSON_CreateArray(), *line = cJSON_CreateArray();
    for (int j = 0; j < 2; j++) {
      cJSON *cells = cJSON_CreateArray();
      for (int k = 0; k < 2; k++) {
        term_t c = var(0, 10);
        dcp_assert(yices_arith_eq_atom(c, yices_int32(i + j + k + n)));
        cJSON_AddItemToArray(cells, dcp_term(c));
      }
      cJSON_AddItemToArray(plane, cells);
      term_t g = yices_new_uninterpreted_term(yices_bool_type());
      dcp_assert(i == j ? g : yices_not(g));
      cJSON_AddItemToArray(line, dcp_term(g));
    }
    cJSON_AddItemToArray(cube, plane);
    cJSON_AddItemToArray(grid, line);
  }
  term_t big = yices_new_uninterpreted_term(yices_int_type());
  dcp_assert(yices_arith_eq_atom(big, yices_int64(30000000000LL + n)));
  dcp_output("cube", cube);
  dcp_output("grid", grid);
  dcp_output("big", dcp_term(big));
}
'''
LARGE = PRELUDE + '''
void build(const cJSON *instance) {
  int n = (int)dcp_int(dcp_get(instance, "n"));
  enum { N = 3000 };
  static term_t b[N], ones[N];
  cJSON *out = cJSON_CreateArray();
  for (int i = 0; i < N; i++) {
    b[i] = yices_new_uninterpreted_term(yices_bool_type());
    ones[i] = yices_ite(b[i], yices_int32(1), yices_int32(0));
    cJSON_AddItemToArray(out, dcp_term(b[i]));
  }
  term_t total = yices_sum(N, ones);
  dcp_assert(yices_arith_eq_atom(total, yices_int32(n)));
  dcp_output("b", out);
  dcp_output("count", dcp_term(total));
}
'''
# Golomb ruler of `marks` marks with every difference distinct, by pairwise inequalities.
def golomb(marks, length, body_tail, name="x"):
    return PRELUDE + f'''
#define MARKS {marks}
void build(const cJSON *instance) {{
  int n = (int)dcp_int(dcp_get(instance, "n"));
  term_t m[MARKS], d[MARKS * MARKS];
  int count = 0;
  for (int i = 0; i < MARKS; i++) m[i] = var(0, {length});
  dcp_assert(yices_arith_eq_atom(m[0], yices_int32(0)));
  for (int i = 0; i + 1 < MARKS; i++) dcp_assert(yices_arith_lt_atom(m[i], m[i + 1]));
  for (int i = 0; i < MARKS; i++)
    for (int j = i + 1; j < MARKS; j++) d[count++] = yices_sub(m[j], m[i]);
  dcp_assert(yices_distinct(count, d));
{body_tail}
}}
'''
UNPROVABLE = golomb(11, 200, '''  term_t x = var(n, 10);
  dcp_minimize(yices_add(yices_mul(yices_int32(1000), x), m[MARKS - 1]));
  dcp_output("x", dcp_term(x));''')
SLOW = golomb(11, 71, '''  term_t y = var(n, n);
  dcp_output("y", dcp_term(y));''')
STEP = PRELUDE + '''
/* Minimise x with x >= n - 1 over 0..n: the optimum is n - 1. */
void build(const cJSON *instance) {
  int n = (int)dcp_int(dcp_get(instance, "n"));
  term_t x = var(0, n);
  dcp_assert(yices_arith_geq_atom(x, yices_int32(n - 1)));
  dcp_minimize(x);
  dcp_output("x", dcp_term(x));
}
'''
UNCOMPILABLE = "this is not C\n"
MALFORMED = PRELUDE + '''
void build(const cJSON *instance) {
  int n = (int)dcp_int(dcp_get(instance, "n"));
  (void)var(0, n);
}
'''
UNSATISFIABLE = PRELUDE + '''
void build(const cJSON *instance) {
  term_t x = var(0, 5);
  dcp_assert(yices_arith_eq_atom(x, yices_int32(0)));
  dcp_assert(yices_arith_eq_atom(x, yices_int32(1)));
  dcp_output("x", dcp_term(x));
}
'''
# isolation: the model probes the container from inside build; a failed probe calls dcp_fail.
ISOLATED = '''#include <arpa/inet.h>
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <netinet/in.h>
#include <poll.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <unistd.h>
#include "dcp.h"

static int reachable(void) {
  int fd = socket(AF_INET, SOCK_STREAM, 0);
  if (fd < 0) return 0;
  fcntl(fd, F_SETFL, O_NONBLOCK);
  struct sockaddr_in address;
  memset(&address, 0, sizeof address);
  address.sin_family = AF_INET;
  address.sin_port = htons(443);
  inet_pton(AF_INET, "1.1.1.1", &address.sin_addr);
  if (connect(fd, (struct sockaddr *)&address, sizeof address) == 0) { close(fd); return 1; }
  if (errno != EINPROGRESS) { close(fd); return 0; }
  struct pollfd waiting = {fd, POLLOUT, 0};
  int error = 0;
  socklen_t length = sizeof error;
  int ready = poll(&waiting, 1, 500) > 0;
  if (ready) getsockopt(fd, SOL_SOCKET, SO_ERROR, &error, &length);
  close(fd);
  return ready && error == 0;
}

static void probe(void) {
  struct stat st;
  if (getuid() == 0) dcp_fail("container runs as root");
  if (stat("/dataset", &st) == 0) dcp_fail("dataset is visible to the candidate");
  DIR *dir = opendir("/input");
  int entries = 0, model = 0, request = 0;
  for (struct dirent *e; dir && (e = readdir(dir));) {
    if (!strcmp(e->d_name, ".") || !strcmp(e->d_name, "..")) continue;
    entries++;
    model += !strcmp(e->d_name, "model.c");
    request += !strcmp(e->d_name, "request.json");
  }
  if (entries != 2 || !model || !request) dcp_fail("unexpected /input");
  FILE *written = fopen("/input/written", "w");
  if (written) dcp_fail("input is writable");
  if (reachable()) dcp_fail("network reachable");
}

void build(const cJSON *instance) {
  probe();
  int n = (int)dcp_int(dcp_get(instance, "n"));
  term_t x = yices_new_uninterpreted_term(yices_int_type());
  term_t y = yices_new_uninterpreted_term(yices_int_type());
  dcp_assert(yices_arith_geq_atom(x, yices_int32(0)));
  dcp_assert(yices_arith_geq_atom(y, yices_int32(0)));
  dcp_assert(yices_arith_eq_atom(yices_add(x, y), yices_int32(n)));
  dcp_output("x", dcp_term(x));
  dcp_output("y", dcp_term(y));
}
'''
ENUMERATION = GOOD
SHAPED_INSTANCE = {"n": 3, "rows": [[4, 5, 6], [], [1]], "mixed": [[3, "c"]], "label": "second",
                   "name": "readiness", "note": "ragged rows, mixed rows, an unused string"}


def main():
    results = {}
    with tempfile.TemporaryDirectory(prefix="dcp_readiness_") as directory:
        temp = Path(directory)

        def candidate(name, source):
            path = temp / f"{name}.c"
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
        result = check("enumeration", ENUMERATION, solution_limit=10)
        results["enumeration"] = result["accepted"] and result["solutions_checked"] == 3
        check("minimization", OPTIMAL_MIN, reference=OPTIMIZING)
        check("maximization", OPTIMAL_MAX, reference=MAXIMIZING)
        check("optimum_enumeration", SUM, reference=SUM_REF, solution_limit=3)
        check("minimization_step_one", STEP, reference=STEP_REF, solution_limit=1)
        check("bool_output", BOOL_OUTPUT, reference=FLAG_REFERENCE, solution_limit=2)
        check("constant_output", CONSTANT_OUTPUT, reference=CONSTANT_REFERENCE)
        check("nested_outputs", NESTED, reference=NESTED_REFERENCE, solution_limit=3)
        check("isolation", ISOLATED)
        check("nonlinear_logic", NONLINEAR, reference=NONLINEAR_REF, solution_limit=3)
        check("malformed_output", MALFORMED, expected={"execution_error", "invalid_output"})
        check("empty_output", UNSATISFIABLE, expected={"no_solution"})
        check("timeout_cleanup", SLOW, expected={"execution_timeout"}, execution_timeout=3)
        check("compilation_error", UNCOMPILABLE, expected={"compilation_error"})

        # Bug-class checks (readiness level 2).
        result = evaluate(candidate("optimization_timeout", UNPROVABLE), "readiness", SOLVER,
                          reference_source=EASY_MIN, execution_timeout=3)
        results["optimization_timeout"] = (result["reason"] == "execution_timeout"
                                           and all(item.get("solutions_received", 0) == 0
                                                   for item in result["instances"]))
        check("output_shapes", SHAPES, reference=SHAPES_REF)
        check("instance_shapes", SHAPED, reference=SHAPED_REF, instances=[SHAPED_INSTANCE], instance_count=2)
        result = evaluate(candidate("error_detail", FAILING), "readiness", SOLVER, reference_source=REFERENCE)
        results["error_detail"] = (result["reason"] == "execution_error"
                                   and "does not support non-linear arithmetic" in json.dumps(result))
        result = evaluate(candidate("bad_term", BAD_TERM), "readiness", SOLVER, reference_source=REFERENCE)
        results["error_detail_builder"] = (result["reason"] == "execution_error"
                                           and "Yices" in json.dumps(result))
        result = evaluate(candidate("segfault", SEGFAULT), "readiness", SOLVER, reference_source=REFERENCE)
        results["crash_detail"] = (result["reason"] == "execution_error" and "SIGSEGV" in json.dumps(result))
        check("stray_stdout", CHATTY)
        result = check("auxiliary_free_distinct", AUXILIARY, solution_limit=10)
        results["auxiliary_free_distinct"] = result["accepted"] and result["solutions_checked"] == 3
        check("large_model", LARGE, reference=LARGE_REF, execution_timeout=120, reference_timeout=120)
        # Objective offsets and negative coefficients, both directions.
        check("objective_offset_minimise", OFFSET_MIN, reference=OFFSET_REF)
        check("objective_offset_maximise", OFFSET_MAX, reference=OFFSET_MAX_REF)
        # Every solution of a small satisfaction problem, exactly once.
        result = check("enumeration_exact_count", ENUMERATION, solution_limit=10)
        # Accepted with a limit of 10 and 3 solutions: the search was exhausted, and no
        # output repeats (the evaluator counts distinct outputs).
        results["enumeration_exact_count"] = result["accepted"] and result["solutions_checked"] == 3
        # All optima of a compound objective, no suboptimal solution.
        result = check("optimal_enumeration_only_optima", SUM, reference=SUM_REF, solution_limit=20)
        results["optimal_enumeration_only_optima"] = result["accepted"] and result["solutions_checked"] == 10

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
