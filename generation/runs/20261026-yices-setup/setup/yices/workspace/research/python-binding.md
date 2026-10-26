# Yices 2 Python bindings: research notes

Scope: official Python bindings for Yices 2 (SRI-CSL). Nothing was installed on the host.
Facts are tagged with the URL they came from. "Not stated" means the source did not say it.

## 1. Package and repository

- PyPI package name: `yices`. Install: `pip install yices`. Latest version shown: 1.1.6, released 18 Dec 2024. Source: https://pypi.org/project/yices/ ; https://github.com/SRI-CSL/yices2_python_bindings (README: "Install the Yices SMT Solver first", then `pip install yices`).
- Repository: https://github.com/SRI-CSL/yices2_python_bindings. Top-level: `yices/` (package), `yices_api.py` (ctypes layer), `test/`, `test_api/`, `examples/`, `setup.py`, `LICENSE` (MIT). Source: https://github.com/SRI-CSL/yices2_python_bindings
- Installed modules: `yices_api` (module, from `yices_api.py`), `yices` (package), console script `yices_python_info` (entry point `yices_api:yices_python_info_main`). Source: README and https://raw.githubusercontent.com/SRI-CSL/yices2_python_bindings/master/setup.py
- Python versions: the README does not state them. `setup.py` declares no `python_requires` and only old classifiers (2.7, 3.4, 3.5, 3.6). Treat the supported Python range as **not stated; test it**. Source: https://raw.githubusercontent.com/SRI-CSL/yices2_python_bindings/master/setup.py
- Licence of the bindings: MIT. Source: https://github.com/SRI-CSL/yices2_python_bindings (LICENSE file link).

## 2. Does it bundle libyices? No.

- The README says to install the Yices SMT Solver first; the wheel does not carry the C library. Source: https://github.com/SRI-CSL/yices2_python_bindings
- `yices_api.py` loads the library at import time with ctypes `CDLL`:
  - `find_library("yices")`; if None, `guess_library_name('yices')` gives `libyices.so` (Linux), `libyices.dylib` (darwin), `libyices.dll` (win32), `cygyices.dll` (Cygwin).
  - It tries the bare name first, then `/usr/local/lib`. If both fail: `YicesAPIException("Yices dynamic library not found.")`.
  - No environment variable is read by the loader (LD_LIBRARY_PATH only appears in the history notes). Source: https://raw.githubusercontent.com/SRI-CSL/yices2_python_bindings/master/yices_api.py (fetched; the first 100k characters were read)
- Version check at import: `yices_recommended_version = '2.6.5'`; it reads the `yices_version` symbol and raises if it does not match. Source: same file. Note: the check is for the shipped `yices_version` in the library; exact acceptance rule (minimum vs. equal) was read as "minimum" by the fetch summary, verify when installing.
- `yices_python_version = '1.1.6'`. Source: same file.
- GMP is loaded lazily in `hasGMP()` (`libgmp`), same find-then-guess pattern. Source: same file.

### How to get libyices (official)

Source: https://yices.csl.sri.com/doc/install-binaries.html
- Debian/Ubuntu: `sudo add-apt-repository ppa:sri-csl/formal-methods`, `sudo apt-get update`, `sudo apt-get install yices2`.
- macOS: `brew install SRI-CSL/sri-csl/yices2`.
- Archives (Linux, macOS, Windows) from https://yices.csl.sri.com ; `sudo ./install-yices` installs to `/usr/local`, or `./install-yices <dir>`. Archives are statically linked against GMP and libpoly. The page does not name `libyices`/`yices.h` explicitly.
- Build from source: https://yices.csl.sri.com/doc/install-sources.html
  - Deps: C99 compiler, GNU make, sed, `libgmp-dev`, `gperf`; git clones also need `autoconf`; MCSAT needs LibPoly and CUDD (`--enable-mcsat`); `--enable-thread-safety` is incompatible with MCSAT.
  - Commands: `sudo apt-get install libgmp-dev gperf; ./configure; make -j; sudo make install` (git clone: first `autoconf`). Optional `make -j check`.
  - Install: binaries `/usr/local/bin`, headers `/usr/local/include`, library `/usr/local/lib` (`--prefix=` changes it).
- Alpine packages `yices2`/`yices2-dev` (2.6.5, GPL-3.0-or-later per the package page): https://pkgs.alpinelinux.org/package/edge/testing/x86/yices2-dev (found via search; not checked).
- Ubuntu/Debian `yices2` via apt was NOT verified against the official Ubuntu archive; the search turned up only `ices2`, a different project.

## 3. Versions and release

- Yices 2 releases (GitHub, newest first): Yices-2.7.0 (marked Latest), 2.6.5, 2.6.4, 2.6.3 (pre-release), 2.6.2, 2.6.1, 2.6.0, 2.5.4, 2.5.3. Year of 2.7.0 not shown on the fetched page. Source: https://github.com/SRI-CSL/yices2/releases
- The bindings' recommended minimum is 2.6.5 (see above). Pin the tested version in the integration, not the skill.
- Licence of yices2 itself: the fetched pages do not state it (the LICENSE URL 404'd). The search summary claimed GPLv3 (Formal Methods listing, https://gitmoss.fyi/fmtools/content/src/branch/main/tools/sat-smt/yices.md) and GPL-3.0-or-later for the Alpine package. **Unverified: check https://github.com/SRI-CSL/yices2 LICENSE before publishing anything.**

## 4. High-level API (`yices` package)

Module: `yices` exports `Config`, `Context`, `Constructors`, `Model`, `Parameters`, `Status`, `Types`, `Terms`, `YicesException`, `Yices`, `Yvals` (README import list). Terms and types are plain integers (`term_t`, `type_t`).

### Config (`yices/Config.py`)
- `Config()` constructor.
- `Config.default_config_for_logic(logicstr)` (e.g. `'QF_LRA'`, `'QF_BV'`, `'QF_NRA'`, shown in README).
- `Config.set_config(key, value)` (wraps `yices_set_config`).
- `Config.dispose()`, static `Config.population()`.

### Context (`yices/Context.py`)
- `Context(config=None)`.
- `assert_formula(term)`, `assert_formulas(seq)`.
- `check_context(params=None, timeout=None)`: `params` is a `Parameters` object (unwrapped to `params.params`). If `timeout` (seconds) is given, a `threading.Timer(timeout, Context.stop_search, [self])` is started and cancelled after the check. Returns the status.
- `check_context_with_assumptions(params, seq)`, `check_context_with_model(params, model, seq)`, `check_context_with_model_and_hint(params, model, seq, hints)`: `params` is required here (not defaulted).
- `stop_search()`, `status()` (method name is `status`, not `context_status`; no error check), `reset_context()`.
- `push()`, `pop()`: return `True`; raise `YicesException('yices_push'|'yices_pop')` on error.
- `get_unsat_core()`, `assert_blocking_clause()`, `enable_option`, `disable_option`, `dispose()`, static `population()`.
- Source: https://raw.githubusercontent.com/SRI-CSL/yices2_python_bindings/master/yices/Context.py (method list and the Timer code quoted above).

### Parameters (`yices/Parameters.py`)
- `Parameters()` (wraps `yices_new_param_record`).
- `set_param(key, value)` (wraps `yices_set_param`), `default_params_for_context(context)` (wraps `yices_default_params_for_context`), `dispose()`, static `population()`.
- Allowed keys are not listed in the bindings; they are the heuristic parameters of the C API: https://yices.csl.sri.com/doc/parameters.html (not read in this run).
- No timeout parameter in the bindings; the timeout is the Python-level `threading.Timer` in `check_context`.

### Status (`yices/Status.py`)
- Constants: `Status.IDLE`, `SEARCHING`, `UNKNOWN`, `SAT`, `UNSAT`, `INTERRUPTED`, `ERROR`; `Status.name(status)` returns the name string.
- Integer values (from `yices_api.py`): IDLE=0, SEARCHING=1, UNKNOWN=2, SAT=3, UNSAT=4, INTERRUPTED=5, ERROR=6.

### Model (`yices/Model.py`)
- `Model.from_context(context, keep_subst)`: built from the context's last model (`yices_get_model`); raises `YicesException` if the model is 0. Call after a SAT result.
- `Model.from_map(mapping)`, `Model()` (new empty model), `dispose()`, static `population()`.
- `get_value(term)`: returns a Python value (bool, int, Fraction, float, list, tuple, callable for functions). Also `get_value_as_term(term)`.
- Typed getters: `get_bool_value(term)`, `get_integer_value(term)`, `get_fraction_value(term)`, `get_float_value(term)`, `get_scalar_value(term)`. Bit-vectors come back as a list of bits via `get_value`. No `get_mpq_value`.
- `formula_true_in_model(term)`, `formulas_true_in_model(terms)`.
- `set_bool`, `set_integer`, `set_fraction`, `set_bv`, `set_bv_from_array`.
- `to_string(width, height, offset)`, `print_to_fd(fd, width=None, height=None, offset=None)`, `print_term_values(...)`.
- `implicant_for_formula(s)`, `generalize_model(...)`, `support_for_term(s)`.
- Source: https://raw.githubusercontent.com/SRI-CSL/yices2_python_bindings/master/yices/Model.py

### Terms and Types (`yices/Terms.py`, `yices/Types.py`)
- Types: `Types.real_type()`, `Types.bv_type(n)` (README). Also `int_type`, `bool_type` (not read in this run, verify).
- Terms:
  - `new_uninterpreted_term(tau, name=None)`, `new_variable(tau, name=None)`, `parse_term(s)`.
  - Arithmetic: `add`, `mul`, `sub`, `sum`, `product`, `arith_geq_atom`, `arith_gt_atom`, `arith_leq_atom`, `arith_lt_atom`, `arith_eq_atom`, `arith_neq_atom`, `rational(n, d)`, `integer(v)`.
  - Boolean: `yand(terms)`, `yor(terms)`, `ynot(term)`, `xor`, `iff`, `implies`, `ite`, `eq`, `neq`, `true()`, `false()`.
  - Bit-vector: `bvconst_integer(nbits, i)`, `bvadd(lhs, rhs)`, `bvsgt_atom(lhs, rhs)`, `bvslt_atom` (README).
  - Renames: `yices_and`→`yand`, `yices_or`→`yor`, `yices_not`→`ynot`, `yices_lambda`→`ylambda`; `yices_bvconst_int64`→`bvconst_integer`; `yices_rational64`→`rational`.
- Source: https://raw.githubusercontent.com/SRI-CSL/yices2_python_bindings/master/yices/Terms.py and the README.
- Gotcha noted in the fetch: `yand`/`yor` test `if not len:` (the builtin), so an empty list is not handled by the fallback. Verify in the probe.

### Examples in the README (official)
- Linear real arithmetic (QF_LRA), bit-vectors (QF_BV), non-linear real arithmetic (QF_NRA): `Config().default_config_for_logic('QF_LRA')` → `Context(cfg)` → `Types.real_type()`, `Terms.new_uninterpreted_term` → `Terms.parse_term` → `ctx.assert_formulas([...])` → `ctx.check_context()` compared with `Status.SAT` → `Model.from_context(ctx, 1)` → `model.to_string` / `model.get_value`.
- Sudoku in three forms (`sudoku.ys`, `sudoku.py`, `sudoku_api.py`), MC-SAT example (low-level API, needs libpoly).
- Source: https://github.com/SRI-CSL/yices2_python_bindings (README and `examples/`).

## 5. Not verified / gaps

- Python version range: not stated anywhere; the classifiers are stale (2.7, 3.4–3.6). Must be probed in the image.
- Timeout semantics: no native timeout API in the bindings. The C API has `yices_stop_search` (documented as callable from a signal handler). The Python timer calls `stop_search` from another thread. Status after interruption should be `INTERRUPTED` (C status enum); not verified by a run.
- `check_context` with no `timeout` and no params: the C call uses `params` = NULL, and the status is set by the search.
- Tests in `test/` and `test_api/` were not read; they would be a good source of working examples.
- The search result also mentioned an OCaml binding `yices2_bindings` (GPL-3.0-only per opam) at https://github.com/SRI-CSL/yices2_ocaml_bindings. Not relevant here.

## 6. Sources (URLs)

- https://pypi.org/project/yices/
- https://github.com/SRI-CSL/yices2_python_bindings
- https://raw.githubusercontent.com/SRI-CSL/yices2_python_bindings/master/README.md (fetched via a summariser)
- https://raw.githubusercontent.com/SRI-CSL/yices2_python_bindings/master/setup.py
- https://raw.githubusercontent.com/SRI-CSL/yices2_python_bindings/master/yices_api.py
- https://raw.githubusercontent.com/SRI-CSL/yices2_python_bindings/master/yices/Context.py
- https://raw.githubusercontent.com/SRI-CSL/yices2_python_bindings/master/yices/Model.py
- https://raw.githubusercontent.com/SRI-CSL/yices2_python_bindings/master/yices/Parameters.py
- https://raw.githubusercontent.com/SRI-CSL/yices2_python_bindings/master/yices/Config.py
- https://raw.githubusercontent.com/SRI-CSL/yices2_python_bindings/master/yices/Status.py
- https://raw.githubusercontent.com/SRI-CSL/yices2_python_bindings/master/yices/Terms.py
- https://yices.csl.sri.com/doc/ (C API index)
- https://yices.csl.sri.com/doc/context-operations.html (push/pop, check_context, stop_search, status, set_config, set_param)
- https://yices.csl.sri.com/doc/install-binaries.html
- https://yices.csl.sri.com/doc/install-sources.html
- https://github.com/SRI-CSL/yices2/releases
- https://pkgs.alpinelinux.org/package/edge/testing/x86/yices2-dev
