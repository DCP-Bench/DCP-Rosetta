# Yices 2: semantics for an agent (research notes)

Research date: 2026-10-26. Every fact carries its source URL. Items marked **UNVERIFIED** are my
inference or come from a secondary source and must be run in a probe before they go into the skill.

## Release, licence, limits

- **Current release: Yices 2.7.0, 16 July 2025.** Official site says so, and the GitHub "latest"
  release tag is `yices-2.7.0`, published 2025-07-16.
  - https://yices.csl.sri.com/ (current version and date)
  - https://yices.csl.sri.com/release-notes.html (2.7.0 on July 16, 2025; 2.6.5 on June 24, 2024)
  - https://github.com/SRI-CSL/yices2/releases (Yices-2.7.0 marked Latest; no newer tag found)
  - GitHub API `repos/SRI-CSL/yices2/releases/latest`: tag `yices-2.7.0`, published 2025-07-16T19:16:07Z.
  - Master branch had commits pushed 2026-10-22, so there are unreleased changes after 2.7.0.
- **Licence: GPLv3.** Official site: "open source software distributed under the GPLv3 license", with
  alternative terms via fm-licensing@csl.sri.com. The repository README badge is "License: GPL v3", and
  the GitHub API reports SPDX `GPL-3.0`.
  - https://yices.csl.sri.com/
  - https://github.com/SRI-CSL/yices2 (README badge; `gh api repos/SRI-CSL/yices2` licence field)
- **No key, no account, no size limit from the licence.** Nothing in the licence or install docs asks
  for a key. The only size limits are structural hard limits, not licence limits:
  - `YICES_MAX_TYPES`, `YICES_MAX_TERMS` = `UINT32_MAX/8` (536,870,911); `YICES_MAX_ARITY`,
    `YICES_MAX_VARS`, `YICES_MAX_BVSIZE` = `UINT32_MAX/16` (268,435,455); `YICES_MAX_DEGREE` =
    `UINT32_MAX/2`. The page calls these "mostly theoretical".
  - https://yices.csl.sri.com/doc/hard-limits.html (values computed by the fetch; the page itself is the
    source of the macro definitions)
- **Install (from source per README):** `autoconf && ./configure && make && sudo make install`, default
  prefix `/usr/local`. Install is not needed for the Docker plan; the note is only for reference.
  - https://github.com/SRI-CSL/yices2 (README, "Quick Installation")
- **Python bindings are separate.** Repository `SRI-CSL/yices2_python_bindings`, MIT licence, on PyPI as
  `yices`. It needs the Yices C library installed separately. It provides two packages, `yices_api`
  (ctypes low-level) and `yices` (Pythonic `Config`, `Context`, `Types`, ...), plus a binary
  `yices_python_info`. README example for `QF_LRA` uses `cfg.default_config_for_logic('QF_LRA')`.
  - https://github.com/SRI-CSL/yices2_python_bindings (README)
  - The README's version string (1.1.3 bindings, Yices 2.6.2 build) is old; check the current PyPI
    version before pinning. **UNVERIFIED** for the current binding version.
- **Bindings list** (from the main README): Java, Python, Go, OCaml. C is the native API.
  - https://github.com/SRI-CSL/yices2 (README line "bindings for Java ... Python ... Go ... OCaml")

## Logics

- Supported SMT-LIB logics, from the official table (quantifier-free only):
  QF_ABV, QF_ALIA, QF_AUFBV, QF_AUFLIA, QF_AX, QF_BV, QF_IDL, QF_LIA, QF_LRA, QF_NIA, QF_NIRA, QF_NRA,
  QF_RDL, QF_UF, QF_UFBV, QF_UFIDL, QF_UFLIA, QF_UFLRA, QF_UFNIA, QF_UFNIRA, QF_UFNRA.
  - Marked **No**: ALIA, AUFLIA, AUFLIRA, AUFNIRA, LIA, LRA, NIA, NRA, UFLRA, UFNIA (all logics with
    quantifiers). The page says "Currently, Yices supports most quantifier-free SMT-LIB logics."
  - https://yices.csl.sri.com/doc/smt-logics.html
- Nonlinear real arithmetic: "supported by using the MCSAT solver of Yices" (same page).
  - https://yices.csl.sri.com/doc/smt-logics.html
- Theories listed on the homepage: uninterpreted functions with equality, linear and nonlinear integer
  and real arithmetic, bitvectors, scalar types, tuples. Input notations: SMT-LIB 2.0 and 1.2, plus
  Yices's own language.
  - https://yices.csl.sri.com/
- Logics added after the table: QF_AUFBVLIA, QF_UFBVLIA (2.6.5), QF_BVLRA (2.6.5, closed issue #514).
  - https://yices.csl.sri.com/release-notes.html
- Quantifiers: supported in the input language ("exists/forall" via `ef-solve` / `--mode=ef`), not in
  the SMT-LIB logics listed above. Issue #657 (closed 2026-07-25) is a crash in `ef-solve` on 2.7.0.
  - https://github.com/SRI-CSL/yices2/issues/657
  - **UNVERIFIED** that quantified input is needed for any Rosetta problem; the skill should say
    "quantifier-free only" unless a probe proves otherwise.

## Optimisation

- **No optimiser in the public API.** The public headers `src/include/yices.h` and
  `src/include/yices_types.h` contain no `minimize`, `maximize`, `optimi`, or `maxsmt` symbol. The
  API reference index lists no optimisation section (Version info, MCSAT, thread safety, contexts,
  models, formula operations, pretty printing, ...).
  - https://github.com/SRI-CSL/yices2/blob/master/src/include/yices.h (raw header, fetched via GitHub API)
  - https://yices.csl.sri.com/doc/index.html (section list; no optimiser section)
  - Repository code search for "minimize", "maxsmt", "optimi" returned only internal MCSAT/solver
    files, none in the public API.
- **Yices 1 had Max-SMT** with weighted assertions. Yices 2 is a redesign; no equivalent is documented.
  - https://yices.csl.sri.com/ (feature overview, listed under Yices 1)
- **Recommended pattern (UNVERIFIED, to run in a probe):** iterative bound tightening.
  1. `yices_check_context` returns SAT; read the objective with `yices_get_model` and `yices_get_int32_value`
     or `yices_get_mpz_value`.
  2. Push a level (`yices_push`), assert `obj < best` (minimise) or `obj > best` (maximise) with
     `yices_assert_formula`, check again.
  3. On SAT, pop and assert the bound at the outer level, or keep it; on UNSAT, the last best is optimal.
  - Alternative: bound literals passed as assumptions with `yices_check_context_with_assumptions`, so
    no push/pop is needed; UNSAT gives a core via `yices_get_unsat_core`.
  - The push/pop and assumption semantics are documented here:
    https://yices.csl.sri.com/doc/context-operations.html and in `src/include/yices.h`
    (`yices_check_context_with_assumptions`, around line 3388).
  - Push/pop and assumptions are documented in context-operations; the optimisation loop itself is
    **not** documented anywhere official. Mark it as the recommended pattern, not a feature.

## Enumeration of all models

- **Blocking clause:** `int32_t yices_assert_blocking_clause(context_t *ctx)`. Header comment: it adds a
  clause that removes the current *truth assignment* from the search space, so the next
  `yices_check_context` produces a different truth assignment or UNSAT. Return 0 on success, -1 on
  error. Error codes: `CTX_INVALID_OPERATION` if the status is not SAT or UNKNOWN;
  `CTX_OPERATION_NOT_SUPPORTED` if the context does not support multiple checks.
  - https://github.com/SRI-CSL/yices2/blob/master/src/include/yices.h (around line 3574-3594)
- **Gotcha:** the blocked object is the *truth assignment of the Boolean atoms*, not the values of
  integer or bitvector variables. Two distinct integer models can share one truth assignment, so a
  bare `yices_assert_blocking_clause` can skip models or under-count. For enumeration over integer or
  bitvector variables, block the variable values explicitly, e.g. assert
  `(not (and (= x v1) (= y v2) ...))` for each model found, over the projection variables of interest.
  **UNVERIFIED** in a probe; the header does not document the interaction.
- Enumeration loop as documented: check, get model, read the values, block, repeat until UNSAT.
  The context needs multi-check support (the default `push-pop` mode is fine).
  - https://yices.csl.sri.com/doc/context-operations.html (default mode push-pop)

## Check results and statuses

- `smt_status_t` values (from `yices_types.h`):
  `YICES_STATUS_IDLE`, `YICES_STATUS_SEARCHING`, `YICES_STATUS_UNKNOWN`, `YICES_STATUS_SAT`,
  `YICES_STATUS_UNSAT`, `YICES_STATUS_INTERRUPTED`, `YICES_STATUS_ERROR`.
  - https://github.com/SRI-CSL/yices2/blob/master/src/include/yices_types.h (around line 79-85)
- Meaning, from the `yices_check_context` comment in `yices.h`:
  - SAT: satisfiable. UNSAT: not satisfiable. UNKNOWN: neither proved nor disproved.
  - INTERRUPTED: search interrupted. In interactive mode the context returns to its pre-check state
    and the flag is reset to IDLE.
  - ERROR: returned without searching when the status is not IDLE or SAT/UNSAT/UNKNOWN
    (error code `CTX_INVALID_OPERATION`).
  - https://github.com/SRI-CSL/yices2/blob/master/src/include/yices.h (around line 3340-3372)
- Model extraction: `yices_get_model(ctx, keep_subst)` requires status SAT or UNKNOWN, otherwise fails
  with `CTX_INVALID_OP`. Use `keep_subst = 1` (recommended). Free with `yices_free_model`.
  Value functions return -1 on failure (`EVAL_UNKNOWN_TERM`, `EVAL_OVERFLOW`).
  - https://yices.csl.sri.com/doc/model-operations.html
  - https://github.com/SRI-CSL/yices2/blob/master/src/include/yices.h (around line 3755-3778)
- `yices_get_model` on an UNKNOWN status returns a partial model: **do not trust values** from it.
  This follows from the UNKNOWN meaning above; **UNVERIFIED** how the model reads in UNKNOWN.
- `yices_get_bool_value`, `yices_get_int32_value`, `yices_get_int64_value`, `yices_get_mpz_value`,
  `yices_get_mpq_value`, `yices_get_rational32_value`, `yices_get_rational64_value`: the documented
  value readers.
  - https://yices.csl.sri.com/doc/model-operations.html
  - `yices_get_integer_value` and `yices_get_rational_value` are **not** in the header (checked).
- Unsat core: `yices_check_context_with_assumptions` plus `yices_get_unsat_core`. After a plain
  check the core is empty. MCSAT does not support unsat cores.
  - https://yices.csl.sri.com/doc/context-operations.html
  - https://github.com/SRI-CSL/yices2/issues/455 (closed 2026-03-01, "UNSAT cores support in mcSAT")
- `yices_stop_search` may be called from a signal handler; an interrupted search leaves the context in
  INTERRUPTED outside interactive mode, and recovery needs `yices_reset_context` or `yices_pop`.
  - https://yices.csl.sri.com/doc/context-operations.html

## Context and configuration

- `yices_new_config()`, `yices_set_config(cfg, name, value)`, `yices_default_config_for_logic(...)`,
  `yices_free_config`, `yices_new_context(cfg)`; `NULL` gives the default config.
  - https://yices.csl.sri.com/doc/context-operations.html
  - https://github.com/SRI-CSL/yices2/blob/master/src/include/yices.h (around line 2901-3020)
- Modes via the `mode` option: `one-shot` (no assertions after check; more preprocessing),
  `multi-checks` (add, never retract), `push-pop` (default), `interactive` (state saved before each
  check).
  - https://yices.csl.sri.com/doc/context-operations.html
- `yices_assert_formula` in one-shot mode fails when the status is SAT or UNKNOWN.
  - https://yices.csl.sri.com/doc/context-operations.html
- Floyd-Warshall solvers (`ifw`, `rfw`) support only one-shot mode.
  - https://yices.csl.sri.com/doc/context-operations.html

## Gotchas from closed GitHub issues (SRI-CSL/yices2)

All closed issues. Dates are closed dates from the GitHub API.

- **#433 "Bug in check-sat-assuming"** (closed 2025-07-08): a `check-sat-assuming` call changed the result
  of a following `check-sat` in the same context (the report shows sat where z3 gives the expected
  answer). Agent lesson: do not mix assumption checks and plain checks on one context without a
  sanity re-run. Closed as fixed (exact fix not read).
  - https://github.com/SRI-CSL/yices2/issues/433
- **#440 "Obviously incorrect model"** (closed 2023-04-25): a QF_UFNIA model was reported as wrong.
  Lesson: do not trust a SAT model without evaluating the assertions on it.
  - https://github.com/SRI-CSL/yices2/issues/440
- **#451 "Bug in model construction from API"** (closed 2024-04-04): models built from API-constructed
  terms (`yices_constant`, uninterpreted sorts) were wrong. Lesson: API-built terms, especially
  uninterpreted sorts, are a risk; compare results with the SMT-LIB text route.
  - https://github.com/SRI-CSL/yices2/issues/451
- **#547 "Unexpected response to get-info :reason-unknown"** (closed 2025-05-17): after a timeout the
  reason was "can't tell" and the context state was off. Lesson: when UNKNOWN, read the reason and do not
  trust the context state.
  - https://github.com/SRI-CSL/yices2/issues/547
- **#613 "MCSAT crashes when generating models for curried functions"** (closed 2026-05-03): crash in
  MCSAT model generation with curried function types (`int -> int -> int`). Lesson: curried or
  higher-order functions are a crash risk on MCSAT; prefer first-order uninterpreted functions.
  - https://github.com/SRI-CSL/yices2/issues/613
- **#616 "Rare crashes while popping a solver frame"** (closed 2026-05-22): crash inside
  `clause_db_gc_sweep` during `pop` under MCSAT (Java binding). Lesson: `pop` is risky on MCSAT in long
  push/pop loops; the bound-tightening loop should keep pops few, or restart the context.
  - https://github.com/SRI-CSL/yices2/issues/616
- **#615 "Yices crashes during interpolation"** (closed 2026-05-08). Interpolation only; not needed for
  modelling.
  - https://github.com/SRI-CSL/yices2/issues/615
- **#552 "Segmentation fault on QF_ANIA instance"** (closed 2026-02-28): crash on 2.6.5 with nested
  arrays. Fixed on master.
  - https://github.com/SRI-CSL/yices2/issues/552
- **#536 "Issues on bool-ranged array"** (closed 2026-02-28). Array modelling with Boolean index type.
  - https://github.com/SRI-CSL/yices2/issues/536
- **#657 "FATAL ERROR: ef-solve failed: unexpected status: model error"** (closed 2026-07-25): a 2.7.0
  crash on a quantified input with an uninterpreted function. Lesson: quantified input can crash;
  avoid quantifiers in the skill's examples.
  - https://github.com/SRI-CSL/yices2/issues/657
- **#410 "QF_LIA performance issue with mod/div"** (closed 2026-07-05): slow `mod`/`div` by constants
  with Boolean encoding (62k atoms for a small problem). Lesson: `mod`/`div` by a variable or a constant
  can blow up the Boolean encoding; try linearising or bounding them, or try another solver.
  - https://github.com/SRI-CSL/yices2/issues/410
- **#417 "\"\" escape sequence not supported in strings"** (closed 2026-07-12) and **#416 "Double quotes
  omitted in echo command response"** (closed 2026-07-06): SMT-LIB string escaping and echo output
  issues in the CLI. Lesson: do not rely on string-literal escapes or echo output.
  - https://github.com/SRI-CSL/yices2/issues/417
  - https://github.com/SRI-CSL/yices2/issues/416
- **#414 "yices_new_uninterpreted_term does not produce an uninterpreted term"** (closed 2026-05-04).
  Lesson: check the term kind when building uninterpreted terms through the API.
  - https://github.com/SRI-CSL/yices2/issues/414
- **#534 "yices_term_to_string() does not escape illegal variable names"** (closed 2025-06-15). Affects
  any name-based output; use fixed, legal identifiers.
  - https://github.com/SRI-CSL/yices2/issues/534
- **#415 "Doesn't always exit immediately on error"** (closed 2026-07-06). CLI error handling; check the
  exit status in the runner, not only the output.
  - https://github.com/SRI-CSL/yices2/issues/415
- **#493 "yices_new_config() leads to segmentation fault"** (closed 2024-03-11). Old; do not reuse a
  config after `yices_free_config`.
  - https://github.com/SRI-CSL/yices2/issues/493
- **#608 "MC-SAT and thread safety"** (closed 2026-03-08): MCSAT is not thread safe before 2.6.5.
  - https://github.com/SRI-CSL/yices2/issues/608
- **#595** (closed 2025-07-16): docs for the parallel portfolio script `utils/yices2_parallel.py`.
  - https://github.com/SRI-CSL/yices2/issues/595

## Other facts for the skill

- Command line: `yices-smt2` reads SMT-LIB 2 (`yices-smt2 file.smt2`). From 2.7.0 SMT2 model output
  is the default. `--mode=ef` for quantified input.
  - https://github.com/SRI-CSL/yices2 (README; release notes for 2.7.0)
  - https://yices.csl.sri.com/release-notes.html
- `get-info :reason-unknown` is supported in the CLI (see #547).
- Parallel portfolio: `utils/yices2_parallel.py --yices PATH -n 4 FILE`.
  - https://github.com/SRI-CSL/yices2 (README "Parallel" section)

## Open questions for the probes

1. Blocking-clause enumeration on integer-valued projections: confirm that an explicit blocking formula
   over values gives the full model count on a small example.
2. Bound-tightening loop: confirm the push/pop loop and the assumption-based variant both produce the
   optimum on a toy minimise problem, and whether `yices_assert_formula` is allowed after a SAT status in
   push-pop mode.
3. UNKNOWN model: confirm whether `yices_get_model` after UNKNOWN returns usable values.
4. Confirm the current Python binding version on PyPI before pinning.
5. Check that the Docker image (built from the 2.7.0 release tarball, or master) matches what the skill
   documents.
