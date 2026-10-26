# Notes for the shared writer: Yices C interface

Image `dcp-eval/yices_c:v1` (Dockerfile `solvers/yices/c/Dockerfile`, placeholder run.py still in place).
Tested: Yices 2.7.0 built from source with MCSAT (libpoly v0.2.1, CUDD 3.0.0), gcc 12.2.0 on Debian bookworm, amd64.
`yices_version` = "2.7.0", `yices_has_mcsat()` = 1. Skill examples: `check_assets.py ... --interface c --image dcp-eval/yices_c:v1` 8/8 pass.
Probes (sources and outputs reproducible) in `probes/c/`. Skill file: `interfaces/c.md` (about 170 lines); assets `assets/c/<8 examples>`.

## Verified facts (each run in the image)
- Link line `cc -std=gnu99 -O2 model.c -o model -lyices` is enough; `-lgmp` is needed only if `<gmp.h>` is used (undefined `__gmpz_init` otherwise). With `-std=c99` setitimer code compiled without warning too.
- `libyices.so` links `libcudd-3.0.0.so.0`, `libpoly.so.0`, `libgmp.so.10`. Without ldconfig/LD_LIBRARY_PATH: `error while loading shared libraries: libyices.so.2.7: cannot open shared object file`.
- Statuses numeric: IDLE 0, SEARCHING 1, UNKNOWN 2, SAT 3, UNSAT 4, INTERRUPTED 5, ERROR 6.
- Builder error: `yices_add(int, bool)` returns -1, code 24 "argument is not an arithmetic term"; passing -1 on gives code 2 (INVALID_TERM) and `yices_assert_formula` rc -1.
- Nonlinear product: `yices_mul(x,y)` builds fine; `yices_assert_formula` in a default context returns -1, code 308, "the context does not support non-linear arithmetic". Context from `yices_default_config_for_logic(cfg,"QF_NIA")` solves it (MCSAT): 91 = 7*13. Assert after SAT works under MCSAT too (R1 for the simple case).
- Assert after SAT in the default (push-pop) context: rc 0, subsequent check correct. Tightening loop (min and max knapsack) ends with UNSAT proving the optimum. Assert after UNSAT then check: still UNSAT, rc 0. push; assert; UNSAT; pop; check gives SAT again (pop after UNSAT works in default mode).
- `yices_get_model` after UNSAT: NULL, code 400 "the context state does not allow operation".
- Output term in no assertion: `get_int64_value` rc 0, value 0; Boolean false (rc 0).
- `get_int64_value` of 100000000000000000000: rc -1, code 604 "eval error: the term value does not fit the expected type"; `yices_get_mpz_value` with gmp.h gives the exact value (30-digit tested).
- `yices_get_int64_value` on a Boolean term: rc -1, `v` left unchanged.
- `yices_distinct(1, ..)` returns a term (2 = true); `yices_distinct(0, ..)` returns -1, code 18 "integer argument must be positive".
- Floor semantics: `yices_idiv(-7,2)` = -4, `yices_imod(-7,2)` = 1.
- `yices_new_variable` term asserted: rc -1, code 300 "assertion contains a free variable".
- `yices_eq(int, bool)` returns -1, "incompatible types".
- Timer: SIGALRM (1 s) handler calling `yices_stop_search(ctx)` interrupted a hard check at 1.002 s, status 5; `yices_get_model` then NULL; a second check returns 6 (ERROR); `yices_reset_context` returns the status to IDLE (0). `yices_stop_search` on an idle/sat context is harmless.
- Segfault when `yices_init()` is forgotten (exit 139) on the first builder call.
- yices_abs, yices_implies, yices_iff, yices_xor2, yices_and2/or2, yices_product, yices_power, yices_square, yices_neg exist and compile; yices_parse_term parses big integers; `yices_pp_term(stdout,...)` prints `(< (+ 1 (* -1 t!3)) 0)`.
- Both orderings of printf arguments: do not put `yices_get_int64_value(.., &v)` and `v` in one printf argument list (unspecified order); noted only as a probe pitfall.
- Independent checks: partition optimal splits counted by Python itertools (10); jobshop optimum 11 checked by Python brute force over machine orders; knapsack 23 by hand.

## Not verified / not taught
- R3 for Python and R9 (Python side) are the other interface's job. R6 32-bit reading, R8 (model after UNKNOWN) and R11/R12 not probed; the skill says "do not use a model from UNKNOWN" (from docs, not run) -- the shared writer should keep that wording as advice only. Check-with-assumptions, binary search, push/pop optimisation: not taught (push/pop not needed).
- PPA `ppa:sri-csl/formal-methods` `yices2-dev` is mentioned in c.md as untested.

## Sources
https://yices.csl.sri.com/doc/ (basic-usage, context-operations, model-operations, term-operations, error-reports, install-sources, smt-logics); https://github.com/SRI-CSL/yices2 (yices.h, tag yices-2.7.0, commit 85cf17e44eac76b5d14b297c09fc9bfecf47ef65); https://github.com/SRI-CSL/libpoly v0.2.1; https://github.com/ivmai/cudd cudd-3.0.0; cJSON 1.7.15 (Debian package libcjson-dev) for the JSON example. No upstream skill used.

## Interface table (C column)
- Package: libyices + yices.h, link -lyices; install: build from source (tarball lacks libcudd), `--enable-mcsat` needs libpoly + CUDD.
- Start/stop: `yices_init()` first (crash otherwise), `yices_exit()` last.
- Operators: none (C). Errors: -1/NULL_TERM returns, cascade; `yices_error_code/yices_error_string/yices_print_error`.
- Time limit: none built in; SIGALRM + `yices_stop_search`. Interrupted context needs `yices_reset_context`.
- Big ints: gmp.h before yices.h, `-lgmp`, `yices_get_mpz_value`. JSON: none built in (cJSON).
- Optimisation: none; tighten with a strict bound in the same context. Enumeration: no-good over outputs, not `yices_assert_blocking_clause` (run in probes/c/blocking.c: x in 1..5 with `yices_assert_blocking_clause` after each model found 1 solution, then the loop stopped: it missed 4).
- Global constraints: only `yices_distinct`. Nonlinear: needs QF_NIA context (MCSAT).
- Docker state: placeholder run.py (`runtime.main("cpp")`) is not the real runner; no driver.c/dcp.h/CONTRACT.md/readiness yet (steps 4+ of the plan).
