# yices_c: how this integration realises the submission contract

Read [the submission contract](../../CONTRACT.md) first; this file only says how Yices 2 (C API)
expresses it. The standalone solver skill is [yices](../skills/yices/SKILL.md), with the C API in
[interfaces/c.md](../skills/yices/interfaces/c.md): it teaches `yices.h`. Runner: [run.py](run.py) compiles
the submission with the C driver [driver.c](c/driver.c), whose helpers are declared in [dcp.h](c/dcp.h).
A skill example is a standalone program; a submission is not (it has no `main` and does not read files).

## Submission file

One C file, `model.c`. It starts with `#include "dcp.h"`, which includes `<gmp.h>`, `<yices.h>` and
`<cjson/cJSON.h>`, and may use the C standard library. It must not define `main`, call `yices_init`,
`yices_exit`, `yices_reset` or any context function, read or write files, print to stdout, or include
other files of yours (only the one submission file is staged).

## Entrypoint

```c
#include "dcp.h"
void build(const cJSON *instance);
```

The driver calls `build` once, after `yices_init()`. The submission creates Yices terms, hands its
constraints, outputs and objective to the functions below, and returns. It must not create or check a
context: the driver owns every context. Terms are global in Yices, so the driver builds a second context
from the same terms when it has to.

| Function | Meaning |
|---|---|
| `term_t dcp_chk(term_t t)` | returns `t`; when `t` is `NULL_TERM` ends the run with `error` and the Yices message |
| `void dcp_assert(term_t f)` | a Boolean term every solution must satisfy (checked with `dcp_chk`) |
| `void dcp_set_logic(const char *l)` | context for a logic such as `"QF_NIA"` (needed for a product of two variables); at most once |
| `cJSON *dcp_term(term_t t)` | an output leaf: an integer or Boolean term |
| `void dcp_output(const char *name, cJSON *tree)` | declares output `name`; `tree` is a leaf, or `cJSON_CreateArray()` containers of trees at any depth. Each name once |
| `void dcp_minimize(term_t t)`, `void dcp_maximize(term_t t)` | the objective, an integer term; at most one call |
| `const cJSON *dcp_get(const cJSON *obj, const char *key)` | an instance field; `error` when missing |
| `long long dcp_int(const cJSON *item)` | an integral number (a Boolean as 0/1), within +-2^53; otherwise `error` |
| `void dcp_fail(const char *fmt, ...)` | ends the run with `error` and this message |

## Instance

`instance` is the instance JSON as a cJSON object, keys as in the brief. Read every size from it:
`cJSON_GetArraySize(dcp_get(instance, "rows"))`, `cJSON_GetArrayItem`, `cJSON_ArrayForEach`. Arrays are
nested cJSON arrays, 0-based as stored; strings are `cJSON_IsString`/`valuestring`. Extra keys (`name`,
`note`) are ignored. cJSON stores numbers as doubles: an integer above 2^53 in the instance loses precision,
and `dcp_int` rejects it. Pass instance data to Yices with `yices_int64`.

## Outputs

Each output name maps to a tree whose leaves are `dcp_term(t)` for a term `t` of type integer or Boolean;
arrays are `cJSON_CreateArray()` filled with `cJSON_AddItemToArray`. A raw `cJSON_CreateNumber` as a leaf is
an `error`; give a constant as `dcp_term(yices_int32(5))`. A real, bit-vector or other term is an `error`
naming the output. Booleans are reported as JSON `true`/`false`.

Integers are read as GMP values and written exactly, so there is no 32- or 64-bit limit (verified with
`30000000000` and a 31-digit constant). An output term that occurs in no assertion reads as 0 (false for a
Boolean); the driver's no-goods then make it vary like any other free output.

## Objective

`dcp_minimize(t)` or `dcp_maximize(t)` with an integer term; no call means a satisfaction problem. A second
call is an `error`. The objective term need not be an output.

## Solving

The driver creates the context (the default configuration, or `yices_default_config_for_logic` when
`dcp_set_logic` was called), asserts the formulas, and checks with a timer armed for the time left. Forced:
one context mode (Yices' default push-pop), no time or other parameter set on it, no assumptions.

| Yices status of `yices_check_context` | Result |
|---|---|
| SAT | a solution |
| UNSAT, first check | `unsat` |
| UNSAT after solutions, or after a SAT with an objective | the search is exhausted: optimum proven / `complete` |
| INTERRUPTED (the deadline), or UNKNOWN at the deadline | `timeout` ("Candidate optimum was not proven" with an objective) |
| UNKNOWN before the deadline, ERROR | `error` ("Yices returned unknown" or "Yices check failed", with Yices's message) |

Optimisation: linear tightening in one context: after each SAT the driver asserts `objective < best`
(`>` when maximising) and checks again; UNSAT proves `best`. Nothing is emitted before the proof: when the
deadline comes first the result is `timeout` with no solution. The tightening can be slow when the objective
has a wide range.

Enumeration (`solution_limit > 1`): for an objective, the driver builds a fresh context with the same formulas
plus `objective == best`. After each solution it asserts a no-good over the declared output leaves only (an
integer leaf differs from its value, a Boolean leaf is negated), so two solutions are distinct only if they
differ in a declared output; outputs already emitted are never emitted twice. `complete` when the next check is
UNSAT; with no non-constant leaf the no-good is false and the run ends `complete`. `yices_assert_blocking_clause`
is not used.

Time: the deadline is `execution_timeout - 0.3 s` (at least 0.1 s). Each check arms `setitimer(ITIMER_REAL)`
for the time left, and the `SIGALRM` handler calls `yices_stop_search`. A submission must not use `SIGALRM`,
`alarm` or `setitimer`. `run.py` also kills the process when it is still running at `execution_timeout` (counted from the candidate's
start, after compilation) and reports `timeout` "C execution exceeded limit", unlike the driver's own
"Candidate optimum was not proven"; it means `build` itself or a step outside a check overran, for example a
slow `build`.

## Compilation

`run.py` compiles `model.c` with `gcc -std=gnu11 -O2 -I/opt/c -I/opt/yices/include model.c /opt/c/driver.o
-L/opt/yices/lib -lyices -lcjson -lgmp -lm` under the compilation budget. A compile or link error (a missing
`build`, a second `main`) is `compilation_error` whose detail is "C compilation failed: " followed by the last 3000 characters of
gcc's stderr (with a leading `...` when cut, so with many errors the first one can be lost: fix the earliest
reported one first). A compile running past the compilation budget is `compilation_error` "Compilation timed out".

## Environment

- Image `dcp-eval/yices_c:v1`, base `python:3.12.11-slim-bookworm` (digest pinned in the Dockerfile).
- Yices 2.7.0 with MCSAT (`yices_has_mcsat()` is true), built from the `yices-2.7.0` tag (commit
  `85cf17e44eac76b5d14b297c09fc9bfecf47ef65`) with libpoly 0.2.1 and CUDD 3.0.0 into `/opt/yices`
  (headers in `/opt/yices/include`, libraries in `/opt/yices/lib`, known to the loader through `ldconfig`).
  GPL-3.0; no key, size limit or registration.
- gcc 12.2.0, GMP 6.2.1, cJSON 1.7.15 (`<cjson/cJSON.h>`). The driver is prebuilt as `/opt/c/driver.o`.
- Run by the evaluator with `--network=none --read-only --user=65534:65534 --cap-drop=ALL` and a 512 MB
  `/tmp` tmpfs (where the candidate is built). Nothing else is writable. No other solvers.
- The Python interpreter only runs the runner; it is not in the solve path.

## Traps

- No `main`, no `yices_init`: both belong to the driver. A second `main` is a link error.
- Never call `exit`, `_exit`, `quick_exit` or `abort`. The run counts as reported only when the driver exits with
  its own status code; any other normal exit is `error` "C process exited with code N before reporting a
  status" with the tail of stderr, and `abort()` shows as `killed by signal SIGABRT`.
- A builder that fails returns `NULL_TERM` (-1), and passing it on hides the first error behind `INVALID_TERM`.
  Wrap builder results in `dcp_chk`, so the run ends with the first Yices message. `dcp_assert` and
  `dcp_term` check their argument too.
- A product of two variables is rejected at assertion time ("the context does not support non-linear
  arithmetic", an `error`) unless the model calls `dcp_set_logic("QF_NIA")`. Linear terms, such as a constant
  times a variable, need no logic.
- `yices_new_variable` is for quantifier binders; use `yices_new_uninterpreted_term` ("assertion contains a
  free variable" otherwise).
- Output leaves must be integer or Boolean terms. A bit-vector or real term is an `error`; there is no
  conversion.
- A crash in the submission (a null pointer, a stack overflow) ends the run as `error` naming the signal
  (`killed by signal SIGSEGV`) with the tail of stderr; solutions already reported stay reported.
- Anything the submission prints, including `yices_pp_term(stdout, ...)`, goes to stderr and is lost to the
  protocol: the driver keeps a private copy of the original stdout for its records and points fd 1 at stderr
  (`dup2(2, 1)`) before `build`.
- Objective ranges are searched linearly. A wide range with a late optimum times out; prefer an objective
  with a tight range, or tighter domains.
- `dcp_set_logic` selects MCSAT for the whole context; MCSAT is slower on linear problems than the default.
- Declared outputs must follow the description's conventions (1-based numbers, Boolean versus 0/1 integer);
  the driver does not shift or convert them.

## Example

The pilot fixture [model_yices_c.c](../../../tests/fixtures/model_yices_c.c) (instance fields `n`, `optimize`;
outputs `x`, `y`):

```c
#include "dcp.h"

void build(const cJSON *instance) {
  int n = (int)dcp_int(dcp_get(instance, "n"));
  int optimize = cJSON_IsTrue(dcp_get(instance, "optimize"));
  term_t x = yices_new_uninterpreted_term(yices_int_type());
  term_t y = yices_new_uninterpreted_term(yices_int_type());
  term_t sum = dcp_chk(yices_add(x, y));
  dcp_assert(yices_arith_geq_atom(x, yices_int32(0)));
  dcp_assert(yices_arith_leq_atom(x, yices_int32(n)));
  dcp_assert(yices_arith_geq_atom(y, yices_int32(0)));
  dcp_assert(yices_arith_leq_atom(y, yices_int32(n)));
  if (optimize) {
    dcp_assert(yices_arith_geq_atom(sum, yices_int32(n)));
    dcp_minimize(sum);
  } else {
    dcp_assert(yices_arith_eq_atom(sum, yices_int32(n)));
  }
  dcp_output("x", dcp_term(x));
  dcp_output("y", dcp_term(y));
}
```
