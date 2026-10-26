# Yices 2 C API: research notes

Scope: C API of Yices 2 (SRI). Nothing installed on the host. Facts are from the
official manual (yices.csl.sri.com/doc), the GitHub repository and its header.
Items marked UNVERIFIED were not confirmed from a source.

## 1. Install

- Latest release found: Yices 2.7.0, released 2025-07-16.
  Source: https://github.com/SRI-CSL/yices2/releases/tag/yices-2.7.0 (date shown as "16 Jul", year taken from the release list; the asset list did not load).
- Linux x86_64 release binary tarball (static GMP):
  `yices-2.7.0-x86_64-pc-linux-gnu-static-gmp.tar.gz`
  https://github.com/SRI-CSL/yices2/releases/download/yices-2.7.0/yices-2.7.0-x86_64-pc-linux-gnu-static-gmp.tar.gz
  Source of the list of tarballs: https://github.com/SRI-CSL/yices2/releases/tag/yices-2.7.0 (via https://yices.csl.sri.com/ download page).
- Other release binaries listed: macOS x86_64 and arm64 (`...-apple-darwin...-static-gmp.tar.gz`). Source: https://yices.csl.sri.com/
- Source tarball: https://github.com/SRI-CSL/yices2/archive/refs/tags/yices-2.7.0.tar.gz
- UNVERIFIED: whether the Linux tarball contains `include/yices.h` and a `libyices.so` (the docs list only `static-gmp` tarballs; no contents list was obtained). Check by listing the tarball in the scratch container before writing the skill.
- Source build (official manual): https://yices.csl.sri.com/doc/install-sources.html
  ```
  ./configure
  make -j
  sudo make install
  ```
  Git clone needs `autoconf` first. Prerequisites: GMP ("the GNU Multiple Precision library") and gperf. Ubuntu packages named in the manual: `libgmp-dev`, `gperf`, `autoconf`. Default install: binaries `/usr/local/bin`, headers `/usr/local/include`, library `/usr/local/lib`; `--prefix=<dir>` to change.
  The manual does NOT mention `--enable-shared`/`--with-pic-gmp` (see the INSTALL note below).
- INSTALL / README (GitHub): https://github.com/SRI-CSL/yices2 and https://raw.githubusercontent.com/SRI-CSL/yices2/master/INSTALL
  - "GMP library version 4.1 or newer"; GCC 4.9+ or clang 3.3+; gperf 3.0+ (README).
  - Quick install: `autoconf`, `./configure`, `make`, `sudo make install`; "binaries and libraries install to /usr/local/" (INSTALL).
  - `--enable-mcsat` needs libpoly and CUDD (INSTALL; manual install-sources page). `--enable-thread-safety` builds a re-entrant library; it is incompatible with `--enable-mcsat` (install-sources page).
  - UNVERIFIED: default of shared vs static library in a source build. The README says the Homebrew install includes the "dynamic library and header files".
- Debian/Ubuntu packages, from the README (https://raw.githubusercontent.com/SRI-CSL/yices2/master/README.md):
  ```
  sudo add-apt-repository ppa:sri-csl/formal-methods
  sudo apt-get install yices2
  sudo apt-get install yices2-dev
  ```
  The `yices2-dev` package provides the library and headers (README). Debian's own archive has no yices2 package (packages.debian.org search returned no results), so the PPA is the Debian/Ubuntu route. The PPA was not tested.
- Homebrew: `brew install SRI-CSL/sri-csl/yices2` (README).
- Version gap: the Debian/Ubuntu PPA version is UNVERIFIED.

## 2. Compile and link

- Include: `#include <yices.h>` (the manual's example uses `#include "yices.h"`). Source: https://yices.csl.sri.com/doc/_downloads/5eafabb16245983173537633b62773e4/example1.c (the page's linked example; fetched as a summary only: includes `<stdlib.h> <stdio.h> <stdbool.h> <inttypes.h> "yices.h"`). The example download itself returned 404 when fetched directly; the content came through the basic-usage page: https://yices.csl.sri.com/doc/basic-usage.html
- Link: `gcc example1.c -o example1 -lyices` (basic-usage page, same URL).
- Header: `src/include/yices.h` (https://github.com/SRI-CSL/yices2/blob/master/src/include/yices.h). It includes `<stdint.h>`, `<stdio.h>`, `"yices_types.h"`, `"yices_limits.h"`. It does NOT include `gmp.h`; GMP-dependent declarations are under `#ifdef __GMP_H__` (raw header, https://raw.githubusercontent.com/SRI-CSL/yices2/master/src/include/yices.h).
- GMP: the Linux release is "static-gmp", so the user should not need `-lgmp` there (inferred from the file name, UNVERIFIED). A source build needs GMP installed at build time; whether the installed library needs `-lgmp` at link time is UNVERIFIED. Practical default: add `-lgmp` if the link fails.
- libpoly/CUDD: only needed for MCSat builds.

## 3. Initialisation

- `void yices_init(void)`: "Global initialization. This function must be called before anything else to initialize Yices's internal data structures." https://yices.csl.sri.com/doc/global-initialization.html#c.yices_init
- `void yices_exit(void)`: "Global cleanup ... It must be called when the API is no longer used to avoid memory leaks." Same page.
- `void yices_reset(void)`: deletes all terms and types and resets the symbol tables. Same page.
- Thread safety: the manual has a "Thread-Safe API" page (https://yices.csl.sri.com/doc/thread-safety.html), not fetched. Build flag `--enable-thread-safety` (see section 1).
- Declarations (raw header): `__YICES_DLLSPEC__ extern void yices_init(void);` / `... yices_exit(void);`

## 4. Types

- `typedef int32_t type_t;` and `typedef int32_t term_t;` (indices into global tables). https://yices.csl.sri.com/doc/api-types.html
- `context_t`, `model_t`, `ctx_config_t`, `param_t`: opaque structs (`typedef struct context_s context_t;` etc.). https://yices.csl.sri.com/doc/api-types.html
- `param_t` fields are NOT public: opaque, set with `yices_set_param`. Source: yices_types.h (raw: https://raw.githubusercontent.com/SRI-CSL/yices2/master/src/include/yices_types.h).
- `term_vector_t`: struct {`uint32_t capacity`, `uint32_t size`, `term_t *data`}. api-types page.
- `smt_status_t` (yices_types.h, raw, verified):
  ```c
  typedef enum smt_status {
    YICES_STATUS_IDLE, YICES_STATUS_SEARCHING, YICES_STATUS_UNKNOWN,
    YICES_STATUS_SAT, YICES_STATUS_UNSAT, YICES_STATUS_INTERRUPTED,
    YICES_STATUS_ERROR
  } smt_status_t;
  ```
  Meanings (api-types page): IDLE = initial state, assertions allowed; SEARCHING = during check; UNKNOWN = inconclusive (e.g. quantifiers); SAT; UNSAT; INTERRUPTED = stopped by `yices_stop_search`; ERROR = operation not allowed on the context.
- Term constructors (`yices_int32`, `yices_add`, `yices_and`, `yices_distinct`, `yices_new_uninterpreted_term`, `yices_parse_term`, `yices_new_uninterpreted_term`): only partly seen; `yices_new_uninterpreted_term` and `yices_parse_term` are referenced on basic-usage page. Full constructor list NOT researched (see Gaps).

## 5. Contexts and configs

Verified in the header (raw) and in https://yices.csl.sri.com/doc/context-operations.html:

- `ctx_config_t *yices_new_config(void);` `void yices_free_config(ctx_config_t *config);`
- `int32_t yices_set_config(ctx_config_t *config, const char *name, const char *value);` (-1 on error: `CTX_UNKNOWN_PARAMETER`, `CTX_INVALID_PARAMETER_VALUE`)
- `int32_t yices_default_config_for_logic(ctx_config_t *config, const char *logic);` (-1 on `CTX_UNKNOWN_LOGIC`, `CTX_LOGIC_NOT_SUPPORTED`; `"NONE"` allowed)
- `context_t *yices_new_context(const ctx_config_t *config);` NULL config = default. Invalid config gives NULL with `CTX_INVALID_CONFIG`.
- `void yices_free_context(context_t *ctx);` Freed automatically on `yices_exit`/`yices_reset` if not called.
- `void yices_reset_context(context_t *ctx);` removes assertions, state -> IDLE.
- `smt_status_t yices_context_status(context_t *ctx);`
- `int32_t yices_context_enable_option(context_t *ctx, const char *option);` and `yices_context_disable_option` (preprocessing, e.g. `break-symmetries`).
- Config names and values (context-operations page): `solver-type` {dpllt, mcsat}; `uf-solver`, `bv-solver`, `array-solver` {none, default}; `arith-solver` {none, ifw, rfw, simplex, default, auto}; `arith-fragment` {IDL, RDL, LRA, LIA, LIRA}; `mode` {one-shot, multi-checks, push-pop, interactive}.
- Use `yices_default_config_for_logic(cfg, "QF_LIA")`-style logic names: SMT-LIB logic name; the exact list of logics was not checked.

## 6. Asserting and checking

- `yices_assert_formula(ctx, f)` (basic-usage example; context-operations page).
- `smt_status_t yices_check_context(context_t *ctx, const param_t *params);` NULL params = defaults. Header-verified declaration. https://yices.csl.sri.com/doc/context-operations.html
- `smt_status_t yices_check_context_with_assumptions(context_t *ctx, const param_t *params, uint32_t n, const term_t t[]);` UNSAT -> `yices_get_unsat_core` for the core.
- `smt_status_t yices_check_context_with_model(...)`: MCSat only.
- `param_t *yices_new_param_record(void);` `void yices_default_params_for_context(const context_t *ctx, param_t *params);` `int32_t yices_set_param(param_t *p, const char *pname, const char *value);` (header, raw). Free function for param records not seen (UNVERIFIED).
- Parameter names (https://yices.csl.sri.com/doc/parameters.html): restart (fast-restart, c-threshold, c-factor, d-threshold, d-factor), clause deletion (r-threshold, r-fraction, r-factor, clause-decay), decisions (var-decay, randomness, branching), theory lemmas, simplex, array solver, model reconciliation, exists/forall (ef-max-iters, ef-gen-mode, ef-max-samples, ef-flatten-iff, ef-flatten-ite). NO time limit and NO conflict limit parameter is documented on that page.

## 7. Models and values

- `model_t *yices_get_model(context_t *ctx, int32_t keep_subst);` Returns NULL on error; the context must be SAT or UNKNOWN, else error `CTX_INVALID_OP`. Snapshot: later context changes do not affect it. Free with `void yices_free_model(model_t *mdl);`. Source: https://yices.csl.sri.com/doc/model-operations.html and raw header.
- `int32_t yices_get_int32_value(model_t *mdl, term_t t, int32_t *val);` 0 on success; -1 if not computable, not integer, or overflows 32 bits (`EVAL_OVERFLOW`). Verified in header (raw) and model-operations page.
- `int32_t yices_get_int64_value(model_t *mdl, term_t t, int64_t *val);` same, 64-bit.
- `int32_t yices_get_bool_value(model_t *mdl, term_t t, int32_t *val);` 0 = false, 1 = true; -1 on failure (`TYPE_MISMATCH` if not Boolean).
- `int32_t yices_get_double_value(model_t *mdl, term_t t, double *val);` arithmetic only (`ARITHTERM_REQUIRED`).
- `int32_t yices_get_mpq_value(model_t *mdl, term_t t, mpq_t val);` only if `gmp.h` included before `yices.h`.
- `int32_t yices_formula_true_in_model(model_t *mdl, term_t f);` returns 1/0/-1.
- `yices_get_value_as_term` exists (constant term); `yices_pp_term(stdout, term, 80, 20, 0)` pretty-prints (basic-usage page; pretty-printing page not fetched).
- Model printing functions (e.g. yices_print_model) were not confirmed.

## 8. Errors

- `error_code_t yices_error_code(void);` returns 0 (no error) or an error constant. Verified in raw header.
- `int32_t yices_print_error(FILE *f);` prints the current error; returns -1 only on write error. Raw header verified.
- `int32_t yices_print_error_fd(int fd);`
- `error_report_t *yices_error_report(void);`
- `void yices_clear_error(void);`
- `char *yices_error_string(void);` caller frees with `yices_free_string`.
- Source: https://yices.csl.sri.com/doc/error-reports.html
- Failing API functions return a special value (negative integer or NULL); details are in the global error report (error-reports page). Which function returns which code is not listed in one place.
- `yices_check_context` on a non-idle or invalid context: returns `YICES_STATUS_ERROR`; check with `yices_error_code()`.
- Pattern from basic-usage page: check each return value; on failure call `yices_print_error(stderr)`; `yices_exit()`.

## 9. Timeouts and interruption

- No time limit parameter is documented in the C API. None found among `param_t` names (parameters page), none in context-operations.
- `void yices_stop_search(context_t *ctx);` "can be called from a signal handler to stop the search after a call to yices_check_context." Header (raw) and context-operations page.
- After interruption: outside `interactive` mode the context enters `YICES_STATUS_INTERRUPTED`; the only way to recover is `yices_reset_context` (or `yices_pop` in push/pop mode). `interactive` mode recovers gracefully. Source: context-operations page.
- Practical timeout pattern (derived, not documented as a recipe): start a timer (`alarm()` with a SIGALRM handler calling `yices_stop_search`, or a second thread calling it when built with `--enable-thread-safety`), then check for `YICES_STATUS_INTERRUPTED`. The signal-handler use is what the manual documents; the handler recipe is UNVERIFIED by running.

## 10. JSON reader in C

- Yices has no JSON facility in its C API (no JSON function or header found in the manual index or `yices.h`; absence checked only in the pages read).
- A C program needs a JSON library (e.g. cJSON, jansson, or a small hand parser). Not researched in depth.
- Yices supplies a term parser `yices_parse_term` (basic-usage page) and an SMT-LIB 2 reader through the yices binary (`yices-smt2`), not the C API; these were only glimpsed.

## 11. Gaps (not yet researched)

- Full list of term constructors (`yices_int32`, `yices_add`, `yices_mul`, `yices_and`, `yices_or`, `yices_not`, `yices_distinct`, `yices_ite`, `yices_new_uninterpreted_term`, `yices_bvconst_*`, `yices_arith_eq_atom`, ...). Needed for the skill; check https://yices.csl.sri.com/doc/term-operations.html.
- Free function for `param_t` records; `yices_free_config` already verified.
- Exact `yices_set_param` names for limits, if any; the parameters page shows none.
- Compiled runtime test: nothing compiled here (no install on the host). Every API claim above must be run in the container before it goes in the skill.
- Tarball contents and shared-library default (see section 1, UNVERIFIED).

## Sources

- https://yices.csl.sri.com/doc/basic-usage.html
- https://yices.csl.sri.com/doc/context-operations.html
- https://yices.csl.sri.com/doc/global-initialization.html
- https://yices.csl.sri.com/doc/error-reports.html
- https://yices.csl.sri.com/doc/model-operations.html
- https://yices.csl.sri.com/doc/api-types.html
- https://yices.csl.sri.com/doc/parameters.html
- https://yices.csl.sri.com/doc/install-sources.html
- https://yices.csl.sri.com/
- https://github.com/SRI-CSL/yices2
- https://github.com/SRI-CSL/yices2/releases/tag/yices-2.7.0
- https://raw.githubusercontent.com/SRI-CSL/yices2/master/src/include/yices.h
- https://raw.githubusercontent.com/SRI-CSL/yices2/master/src/include/yices_types.h
- https://raw.githubusercontent.com/SRI-CSL/yices2/master/INSTALL
- https://raw.githubusercontent.com/SRI-CSL/yices2/master/README.md
