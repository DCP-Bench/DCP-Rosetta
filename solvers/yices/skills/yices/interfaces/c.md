# Yices in C (libyices, `yices.h`)

The native API of Yices 2: a C library, declared in `yices.h`, linked as `-lyices`.
Shared concepts, statuses and enumeration strategy: [SKILL.md](../SKILL.md).

## Install

Needs a C compiler and the Yices 2 library with its header. The release tarball for Linux
links `libcudd-3.0.0.so.0`, which it does not ship, so build from source (add
`--enable-mcsat` only after installing libpoly and CUDD, which nonlinear arithmetic needs):

```bash
# prerequisites: gcc make autoconf gperf libgmp-dev git (plus cmake and libtool for libpoly/CUDD)
latest() { git ls-remote --tags --refs "$1" "$2" | sed 's#.*/##' | sort -V | tail -1; }   # newest release tag
git clone --branch "$(latest https://github.com/SRI-CSL/yices2.git 'yices-2.*')" https://github.com/SRI-CSL/yices2.git
cd yices2 && autoconf && ./configure --enable-mcsat --prefix=/opt/yices && make -j && make install
# header in /opt/yices/include, libraries in /opt/yices/lib: make the loader find them (ldconfig or LD_LIBRARY_PATH)
printf '#include <stdio.h>\n#include <yices.h>\nint main(void){puts(yices_version);return 0;}' > v.c
cc -I/opt/yices/include v.c -L/opt/yices/lib -lyices -o v && ./v      # prints the version
```

Ubuntu offers `ppa:sri-csl/formal-methods` with `yices2-dev` (not tested here). Yices is GPL-3.0; no key or
size limit. Build line used below: `cc -std=gnu99 -O2 -I/opt/yices/include model.c -o model -L/opt/yices/lib -lyices [-lcjson]`
(drop `-I`/`-L` when the prefix is on `C_INCLUDE_PATH`/`LIBRARY_PATH` or in a system directory; a missing
`yices.h` means the prefix is not searched). Add `-lgmp` only when you include `<gmp.h>` (before `yices.h`) to read
big values, and `-lcjson` for JSON (Debian/Ubuntu: `apt install libcjson-dev`, header `<cjson/cJSON.h>`).
Details: [installing from source](https://yices.csl.sri.com/doc/install-sources.html)

## Quick start

```c
#include <stdio.h>
#include <yices.h>

int main(void) {
  yices_init();                                   /* first call of any program */
  term_t x = yices_new_uninterpreted_term(yices_int_type());   /* a decision variable */
  term_t y = yices_new_uninterpreted_term(yices_int_type());
  context_t *ctx = yices_new_context(NULL);       /* NULL: default configuration */
  yices_assert_formula(ctx, yices_arith_geq_atom(x, yices_int32(1)));
  yices_assert_formula(ctx, yices_arith_leq_atom(x, yices_int32(5)));
  yices_assert_formula(ctx, yices_arith_eq_atom(yices_add(x, y), yices_int32(7)));
  yices_assert_formula(ctx, yices_arith_gt_atom(x, y));

  if (yices_check_context(ctx, NULL) == YICES_STATUS_SAT) {
    model_t *mdl = yices_get_model(ctx, 1);       /* keep_subst = 1 */
    int64_t vx, vy;
    if (yices_get_int64_value(mdl, x, &vx) == 0 && yices_get_int64_value(mdl, y, &vy) == 0)
      printf("x=%lld y=%lld\n", (long long)vx, (long long)vy);
    yices_free_model(mdl);
  }
  yices_free_context(ctx);
  yices_exit();
  return 0;
}
```

## Modelling

API reference: [term operations](https://yices.csl.sri.com/doc/term-operations.html). Terms are `int32_t`
handles in a global table; a builder that fails returns `NULL_TERM` (-1).

| Need | API |
|---|---|
| integer / Boolean decision variable | [`yices_new_uninterpreted_term(yices_int_type())`](https://yices.csl.sri.com/doc/term-operations.html#c.yices_new_uninterpreted_term), `yices_new_uninterpreted_term(yices_bool_type())`; name with `yices_set_term_name` |
| constants | [`yices_int32`](https://yices.csl.sri.com/doc/term-operations.html#c.yices_int32), `yices_int64` (both return a term; -1 on failure like any builder), `yices_true()`, `yices_false()`, `yices_parse_term("123456789012345678901")` for big ones |
| bounds, comparison | [`yices_arith_geq_atom`](https://yices.csl.sri.com/doc/term-operations.html#c.yices_arith_geq_atom), `_leq_atom`, `_lt_atom`, `_gt_atom`, `_eq_atom`, `_neq_atom` (all `(t1, t2)`) |
| sum, difference, product | [`yices_add(a,b)`](https://yices.csl.sri.com/doc/term-operations.html#c.yices_add), `yices_sub`, `yices_sum(n, arr)`, `yices_mul(a,b)`, `yices_product(n, arr)`, `yices_neg`; a constant times a variable (`yices_mul(yices_int32(3), x)`) is linear and fine in the default context, only variable times variable needs `QF_NIA` |
| div / mod / abs | [`yices_idiv`](https://yices.csl.sri.com/doc/term-operations.html#c.yices_idiv), `yices_imod` (floor: -7 div 2 = -4, -7 mod 2 = 1), `yices_abs` |
| all different | [`yices_distinct(n, arr)`](https://yices.csl.sri.com/doc/term-operations.html#c.yices_distinct), n >= 1 (n = 0 is an error) |
| and / or / not | [`yices_and(n, arr)`](https://yices.csl.sri.com/doc/term-operations.html#c.yices_and), `yices_or(n, arr)`, `yices_and2`, `yices_or2`, `yices_not` |
| implication, equivalence, xor | [`yices_implies`](https://yices.csl.sri.com/doc/term-operations.html#c.yices_implies), `yices_iff`, `yices_xor2` |
| reified condition as 0/1 | [`yices_ite(cond, yices_int32(1), yices_int32(0))`](https://yices.csl.sri.com/doc/term-operations.html#c.yices_ite), then `yices_sum` (counting, element, max) |
| generic equality | [`yices_eq(a, b)`](https://yices.csl.sri.com/doc/term-operations.html#c.yices_eq), `yices_neq`; both sides must have the same type (int vs Boolean gives "incompatible types") |
| table, no-overlap, cumulative | no global constraints: `yices_or` of `yices_and`s; pairwise `yices_or` of two `yices_arith_leq_atom`; per-time `yices_sum` of `yices_ite` |
| minimise / maximise | no optimiser: loop with a strict bound, see below |
| read data from a file | no JSON in Yices: [cJSON](https://github.com/DaveGamble/cJSON) (`#include <cjson/cJSON.h>`, `-lcjson`), see below and [maximise-knapsack-json](../assets/c/maximise-knapsack-json/README.md) |

Check every builder result: an error returns -1, and passing -1 on gives further errors (`INVALID_TERM`) that hide
the first one. Keep a helper such as `term_t chk(term_t t) { if (t < 0) { yices_print_error(stderr); exit(1); } return t; }`.

Reading JSON with cJSON (read the file into a NUL-terminated buffer first):

```c
cJSON *root = cJSON_Parse(text);                                    /* NULL on a syntax error */
cJSON *arr = cJSON_GetObjectItemCaseSensitive(root, "weights");     /* NULL when the key is missing */
int n = cJSON_GetArraySize(arr);
for (int i = 0; i < n; i++) w[i] = (int)cJSON_GetNumberValue(cJSON_GetArrayItem(arr, i));
int cap = (int)cJSON_GetNumberValue(cJSON_GetObjectItemCaseSensitive(root, "capacity"));
cJSON_Delete(root);
```

**Context for nonlinear arithmetic.** Building `yices_mul(x, y)` of two variables succeeds, `yices_assert_formula`
then fails with "the context does not support non-linear arithmetic". Create the context from a logic:

```c
ctx_config_t *cfg = yices_new_config();
yices_default_config_for_logic(cfg, "QF_NIA");   /* MCSAT; see yices_has_mcsat() */
context_t *ctx = yices_new_context(cfg);
yices_free_config(cfg);
```

## Solving

Details: [context operations](https://yices.csl.sri.com/doc/context-operations.html), [model operations](https://yices.csl.sri.com/doc/model-operations.html).

Status of `yices_check_context(ctx, NULL)`, an `smt_status_t`:

| Status | Meaning |
|---|---|
| `YICES_STATUS_SAT` | satisfiable: read a model |
| `YICES_STATUS_UNSAT` | proven unsatisfiable; `yices_get_model` returns NULL (error `CTX_INVALID_OPERATION`) |
| `YICES_STATUS_UNKNOWN` | undecided (incomplete theory); do not use a model from it |
| `YICES_STATUS_INTERRUPTED` | stopped by `yices_stop_search`; the context must be reset |
| `YICES_STATUS_ERROR` | operation not allowed (such as checking an interrupted context) |

Reading values: `yices_get_int64_value(mdl, t, &v)` and `yices_get_bool_value(mdl, t, &b)` (`int32_t b`) return 0 on
success and -1 on failure; `v` is then left unchanged, so test the return value. An output term that occurs in no
assertion reads as 0 (false for Booleans), but a compound term (a sum of `yices_ite` terms, say) is
evaluated from the values of its variables, so read an objective straight from its sum term. Values beyond int64 fail with "eval error: the term value does not fit the
expected type": include `<gmp.h>` before `<yices.h>`, link `-lgmp`, and use `yices_get_mpz_value`. Free every
`model_t` (`yices_free_model`), context, config and parameter record.

Optimise by tightening: after each SAT, read the objective and assert `obj < best` (minimise) or `obj > best`
(maximise) in the same context with `yices_assert_formula`; assertions after a SAT check are allowed. UNSAT then
proves `best` optimal; a limit means the last `best` is only the best found. Example:
[minimise-colouring](../assets/c/minimise-colouring/README.md).

**Time limit.** No parameter exists. Arm a timer whose handler calls `yices_stop_search(ctx)` (safe in a signal
handler), run the check, disarm. The check returns `YICES_STATUS_INTERRUPTED`; the context only accepts
`yices_reset_context(ctx)` afterwards. Complete code: [schedule-jobshop](../assets/c/schedule-jobshop/README.md).

```c
#include <signal.h>
#include <sys/time.h>
static context_t *running;
static void on_alarm(int sig) { (void)sig; yices_stop_search(running); }
/* before the check: running = ctx; signal(SIGALRM, on_alarm);
   setitimer(ITIMER_REAL, &(struct itimerval){{0,0},{10,0}}, NULL);   after: disarm with zeros */
```

## All solutions

Here `out[0..N-1]` are the `N` output terms, all integer (or all Boolean):

```c
enum { N = 8 };                 /* number of output terms */
term_t out[N];                  /* filled while building the model */
term_t differs[N];
smt_status_t st;
while ((st = yices_check_context(ctx, NULL)) == YICES_STATUS_SAT) {
  model_t *mdl = yices_get_model(ctx, 1);
  for (int i = 0; i < N; i++) {
    int64_t v;
    yices_get_int64_value(mdl, out[i], &v);
    printf("%lld ", (long long)v);
    differs[i] = yices_arith_neq_atom(out[i], yices_int64(v));   /* Boolean output: see below */
  }
  yices_free_model(mdl);
  yices_assert_formula(ctx, yices_or(N, differs));                /* no-good over the outputs only */
}
/* st == YICES_STATUS_UNSAT: complete */
```

For a Boolean output read `int32_t b` with `yices_get_bool_value(mdl, out[i], &b)` and use
`differs[i] = b ? yices_not(out[i]) : out[i];`.

For all optimal solutions find the optimum first, then build a new context from the same terms (terms are global)
with `obj == best` and run this loop. Examples: [all-solutions-queens](../assets/c/all-solutions-queens/README.md),
[all-optimal-partition](../assets/c/all-optimal-partition/README.md).

## Common issues

| Problem | Likely cause | Fix |
|---|---|---|
| segmentation fault at the first call | `yices_init()` missing | call it first, `yices_exit()` last |
| `libyices.so.2.7: cannot open shared object file`, `libcudd-3.0.0.so.0` missing | library directory not known to the loader; or the release tarball, which lacks CUDD | `ldconfig` or `LD_LIBRARY_PATH`; build from source (Install) |
| `assertion contains a free variable` (code 300) | used `yices_new_variable`, which is for quantifier binders | `yices_new_uninterpreted_term` |
| `the context does not support non-linear arithmetic` (code 308) | product or division of variables in a default context | create the context for `QF_NIA` (Modelling) |
| `argument is not an arithmetic term` (24), then errors with code 2 (`INVALID_TERM`) | a type mismatch returned -1 and the -1 was passed on | check each builder result, print the first error |
| `incompatible types` from `yices_eq` | integer compared with Boolean | compare terms of one type; use `yices_ite` to turn a condition into 0/1 |
| `integer argument must be positive` from `yices_distinct` | called with no terms | skip the constraint when n = 0 |
| `the context state does not allow operation` (code 400) | model requested after UNSAT or INTERRUPTED, or check on an interrupted context | test the status; `yices_reset_context` after INTERRUPTED |
| enumeration repeats or misses solutions | `yices_assert_blocking_clause` blocks the Boolean atom assignment, not integer values | assert a no-good over the output terms (All solutions) |
| garbage value after `yices_get_int64_value` | return value -1 ignored, `v` unchanged | check the return code; big values need `yices_get_mpz_value` |
| `undefined reference to symbol '__gmpz_init'` and `DSO missing from command line` | `<gmp.h>` included without `-lgmp` | add `-lgmp` |

## Runnable examples

- [satisfy-magic-square](../assets/c/satisfy-magic-square/README.md): bounded integers, distinct, sums, reading a model
- [all-solutions-queens](../assets/c/all-solutions-queens/README.md): no-good enumeration until UNSAT
- [all-optimal-partition](../assets/c/all-optimal-partition/README.md): minimise, then enumerate every optimum in a fresh context
- [maximise-knapsack-json](../assets/c/maximise-knapsack-json/README.md): maximise, instance read from JSON with cJSON
- [minimise-colouring](../assets/c/minimise-colouring/README.md): minimise with 0/1 usage flags
- [infeasible-pigeonhole](../assets/c/infeasible-pigeonhole/README.md): UNSAT as a result
- [schedule-jobshop](../assets/c/schedule-jobshop/README.md): disjunctive scheduling, makespan, time limit
- [nonlinear-product](../assets/c/nonlinear-product/README.md): QF_NIA / MCSAT and the default-context error
