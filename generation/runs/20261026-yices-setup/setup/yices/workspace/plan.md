# Yices 2 setup plan (C API + Python bindings)

Run 20261026-yices-setup, branch add-yices. Nothing here has been run yet. Every behaviour marked PROBE must be run in the image before it is written into the skill, a contract or a runner. Where the council disagreed, the decision and the reason are given inline ("Decision").

## 0. Layout (fixed)

- Skill: `solvers/yices/skills/yices/` (SKILL.md, interfaces/c.md, interfaces/python.md, assets/c/<ex>/, assets/python/<ex>/, sources.md, evals/evals.json). Review result goes to `solvers/yices/standalone-review.json`.
- Integrations: `solvers/yices/c/` (id `yices_c`, image `dcp-eval/yices_c:v1`), `solvers/yices/python/` (id `yices_python`, image `dcp-eval/yices_python:v1`).
- Evidence: `generation/runs/20261026-yices-setup/setup/<id>/setup-001/`. Workspace: this folder.
- Skill metadata: `paradigm: smt`, `interfaces: "c, python"`, no `related-skills` (no source or companion found; the existing-skills search found nothing usable).

## 1. Yices version and licence

- **Yices 2.7.0** (released 2025-07-16, latest tag) in both images. Python bindings `yices==1.1.6` (MIT per the bindings repo LICENSE; PyPI metadata says GPLv3; check the wheel's own METADATA/LICENSE in the probe and record both in sources.md). Yices core: GPL-3.0-or-later (README in the tarball). No key, no account, no size limit.
- The skill stays unpinned; sources.md records 2.7.0 / 1.1.6 as tested. The bindings' recommended libyices is 2.6.5; PROBE that 1.1.6 imports and works against 2.7.0.

## 2. Docker approach

**Decision: build Yices 2.7.0 from source with MCSAT, in both images; do not use the official binary tarball and not the PPA.**
Why: the infrastructure council inspected the tarball (`yices-2.7.0-x86_64-pc-linux-gnu-static-gmp.tar.gz`). Its `libyices.so.2.7.0` has `NEEDED libcudd-3.0.0.so.0`, which the tarball does not ship and bookworm does not package; it has no `libyices.so` symlink; libpoly and CUDD are not in bookworm. The teachability council's default (tarball + `install-yices`) therefore fails, and MCSAT (needed for nonlinear integer products, common in benchmark models) is required. The PPA is Ubuntu-only and its version is unknown.

Shared build stage, byte-identical in both Dockerfiles so the layer cache is shared (no common base image because `evaluation.build` builds each id alone). Keep the two copies in sync:

- `FROM python:3.12.11-slim-bookworm@sha256:519591d6871b7bc437060736b9f7456b8731f1499a57e22e6c285135ae657bf7 AS yices-build`
- apt, pinned: gcc 4:12.2.0-3, g++ 4:12.2.0-3, make 4.3-4.1, cmake 3.25.1-1, autoconf 2.71-3, automake 1:1.16.5-1.3, libtool 2.4.7-7~deb12u1, gperf 3.1-1, libgmp-dev 2:6.2.1+dfsg1-1.1, git, ca-certificates.
- libpoly v0.2.1 (clone, check rev-parse == 3d5e6fbd98639cb0941b029e23ca17c0e3c4a80a; cmake; prefix /opt/yices).
- CUDD cudd-3.0.0 from github.com/ivmai/cudd (rev-parse == f54f533303640afd5dbe47a05ebeabb3066f2a25; `autoreconf -fi; ./configure --enable-shared --prefix=/opt/yices`).
- Yices tag yices-2.7.0 (rev-parse == 85cf17e44eac76b5d14b297c09fc9bfecf47ef65; `autoconf; CPPFLAGS=-I/opt/yices/include LDFLAGS=-L/opt/yices/lib ./configure --enable-mcsat --prefix=/opt/yices; make -j2; make install`).
- Pin by commit check (as highs_cpp does), not by archive checksum. Record the source archive sha256 `584db72abf6643927b2c3ba98ff793f602216b452b8ff2f34a8851d35904804a` in sources.md as information only.
- Fallback if libpoly v0.2.1 or this CUDD build is rejected by configure: use the libpoly tag that Yices's own `.github/actions/build/action.yml` uses.

Final images (both: same digest-pinned python:3.12.11-slim-bookworm; `COPY --from=yices-build /opt/yices /opt/yices`; `echo /opt/yices/lib > /etc/ld.so.conf.d/yices.conf && ldconfig`; apt `libgmp10=2:6.2.1+dfsg1-1.1`):

- **yices_c**: add gcc 4:12.2.0-3 and `libcjson-dev=1.7.15-1+deb12u4` (pinned). No cmake. `COPY solvers/yices/c/c /opt/c` (dcp.h, driver.c); compile `driver.c` to `driver.o` at build time; smoke step compiles and runs a `yices_version` program so a bad link fails `docker build`. Copy `runner/runtime.py` and `solvers/yices/c/run.py` to /opt/runner; ENTRYPOINT `python /opt/runner/run.py`.
- **yices_python**: only libgmp10 beyond the Yices copy; `pip install --require-hashes yices==1.1.6` (wheel `yices-1.1.6-py3-none-any.whl`, sha256 030321a6a926a7992cb380cd597f2df81f06c56644daad790c7e832d2cd4a780). Smoke: `python -c "from yices import Yices; print(Yices.version())"`. No shared CP requirements (like cvc5_python). Runner files copied as for C.
- Skill tests run in these images too (skill examples use `-lcjson` for C; the image carries cjson-dev, so the skill's C build line is `cc -std=c99 -O2 model.c -o model -lyices -lcjson` plus `-lgmp -lm` if the PROBE shows they are needed). Image paths and facts stay out of the skill; they go in each CONTRACT.md.

## 3. Interface table rows (SKILL.md)

| Row | C | Python |
|---|---|---|
| Read | interfaces/c.md | interfaces/python.md |
| Package | libyices + `yices.h`, link `-lyices` | pip `yices` (does not bundle libyices; install the library first) |
| Install | build from source with MCSAT; the official Linux tarball needs `libcudd-3.0.0.so.0` which it does not ship; PPA `yices2-dev` on Ubuntu is a one-line alternative | after libyices: `pip install yices`; run `ldconfig` so `find_library('yices')` or `/usr/local/lib` finds it |
| Start/stop | `yices_init()` first, `yices_exit()` last | PROBE whether import initialises; `Yices.exit()` optional |
| Naming | `yices_<op>`, n-ary ops `(n, term_t[])`, `yices_and2`/`or2` helpers | `Terms.<op>` static methods on lists; `yand/yor/ynot/yxor` |
| Operators | none | none: no operator overloading, `x + 1` is not a term (PROBE what it does) |
| Errors | builders return `NULL_TERM` (-1) or negative; errors cascade; `yices_error_code()`, `yices_error_string()` | `YicesException` at the call |
| Reading values | `yices_get_int64_value(mdl,t,&v)` returns 0/-1, `v` unset on failure; free model | `Model.from_context(ctx,1)`, `get_value`, `get_bool_value` |
| Time limit | `setitimer`/`alarm` + SIGALRM handler calling `yices_stop_search(ctx)` | `ctx.check_context(timeout=s)` (Timer thread calling stop_search) |
| Big integers | include `<gmp.h>` before `yices.h` for mpz readers | Python ints |
| Memory | free config, params, model, context | `dispose()` on Config, Parameters, Context |
| JSON | none built in: cJSON (`<cjson/cJSON.h>`, `-lcjson`) | stdlib `json` |

Default binding when unspecified: the project's language; else Python.

## 4. Modelling and solving content

**SKILL.md (shared):** Yices is an SMT solver; "variable" in the API means a quantifier-bound variable, decision variables are *uninterpreted terms* from a type (main naming trap). No global constraints, no optimiser. Integers unbounded, bound them from the data. Logic choice: default context (DPLL(T), linear arithmetic, BV, UF, arrays); nonlinear products need MCSAT via a logic such as QF_NIA (check `yices_has_mcsat()`). Modelling table concept to encoding (all-different = distinct, sum, count = sum of ite, max/min = ite, element = ite chain, table = or of ands, no-overlap = pairwise disjunction, cumulative = per-time sum of ite, distinct count = used flags); exact names in interface files. Statuses SAT, UNSAT, UNKNOWN, INTERRUPTED, ERROR; model readable after SAT (UNKNOWN: PROBE usability); after INTERRUPTED the context must be reset.

**Optimisation pattern. Decision:** the skill teaches one default, linear solution-improving search on a single context with a strict bound on the integer objective (`obj < best`, or `>` when maximising); UNSAT after a SAT proves `best`; INTERRUPTED means not proven. Council disagreement: teachability wanted push/pop (so the context can be reused to enumerate all optima), correctness/infra wanted permanent asserts (avoiding #616 pop crash under MCSAT, #433 assumptions bug). Decision: the skill teaches **push/pop for the tightening step only when PROBE R1 shows it is correct in the default mode, and always teaches "enumerate all optima in a fresh context built from the same terms plus `obj == best`"** (terms are global in Yices, so a rebuild is cheap). That avoids relying on pop after UNSAT and works under MCSAT. If R1 shows assert-after-SAT is illegal in push-pop mode, switch to `mode=multi-checks` in the config, or one fresh context per bound, and say so. Check-with-assumptions is not taught. Binary search is not taught.

**Enumeration. Decision (all agree):** never use `yices_assert_blocking_clause` for integer outputs (it blocks the Boolean atom assignment). Assert a no-good `or(x_i != v_i)` over the output variables only (`arith_neq_atom` for ints, `neq` for Booleans; `false` if no output is non-constant). Loop until UNSAT (complete). The skill explains the blocking-clause trap in Common issues with a runnable example.

**Timeouts:** no time-limit parameter exists. C: arm `setitimer(ITIMER_REAL)`, SIGALRM handler calls `yices_stop_search(ctx)` (documented signal-safe). Python: `check_context(timeout=)`; a Python signal handler cannot interrupt a ctypes call so it is only a backstop. PROBE R3/R4 first.

**Common issues to seed (each only after a probe gives the exact text):** new_variable vs new_uninterpreted_term; nonlinear term in default context; assert after UNSAT; distinct with <2 args; div/mod semantics; no model after INTERRUPTED; C: missing `yices_init`, NULL_TERM cascade, unchecked get_int64 return, `libyices.so` not found (ldconfig), mpz readers need `gmp.h` first; Python: "Yices dynamic library not found", Z3-style operators, `and_` vs `yand`, Status compared to string, `from_context` raising after UNSAT, `libcudd` missing from the binary tarball.

## 5. Examples (same eight names per interface)

`assets/c/<ex>/{model.c,README.md}` and `assets/python/<ex>/{model.py,README.md}`; JSON example also has `data.json`:

1. satisfy-magic-square (uninterpreted int terms, bounds, distinct, sums, reading values)
2. all-solutions-queens (no-good over outputs; last status UNSAT)
3. all-optimal-partition (tighten, then fresh context with `obj == best`, enumerate)
4. maximise-knapsack-json (path from argv else bundled data.json; sizes from data, ragged lists, extra keys ignored; cJSON in C, `json` in Python)
5. minimise-colouring (used flags; minimise sum)
6. infeasible-pigeonhole (UNSAT reported, not raised)
7. schedule-jobshop (pairwise disjunction, makespan, time limit, "optimal" vs "best found, not proven", INTERRUPTED then reset; carries the timeout recipe)
8. nonlinear-product (QF_NIA/MCSAT; also shows the error in the default context). Kept because the image has MCSAT; dropped if the probe shows otherwise.

Validate with `check_assets.py <skill> --interface c|python --image dcp-eval/yices_<i>:v1`. Interface length: each interface file under about 200 lines. C is at risk. **Decision:** keep timer and JSON code in assets; if `c.md` still passes 200 lines, use the template's folder form `interfaces/c/README.md` plus `json.md` (the template allows this; the fixed layout change is just the interface entry, report it).

`evals/evals.json`: one prompt per toy family per interface (14), two that name only "Yices" (routing test), three negatives (n-queens with Z3 Python, cvc5 knapsack, SMT-LIB benchmark shell task). Assertions: reads the right interface file, uses `new_uninterpreted_term`, tightening with UNSAT as proof, no-good over outputs.

## 6. Integration design (both)

**Common contract (decisions):**
- Submission creates terms only; the runner owns every context (terms are global, Yices cannot list a context's assertions; avoids relying on pop). Submission never calls `yices_init/exit/reset` (contract trap; document).
- Default context built from a config with `mode` push-pop; logic only if the submission requests one (`QF_NIA` selects MCSAT). 
- Results: SAT -> model; first-check UNSAT -> `unsat`; after solutions UNSAT -> optimum proven / `complete`; INTERRUPTED -> `timeout`; UNKNOWN -> `timeout` if past deadline else `error` ("yices returned unknown" plus error string), a model from UNKNOWN is never used; ERROR -> `error` with the Yices message.
- Models read with `keep_subst=1`. Output leaves and objective must be int or bool terms (checked with `yices_term_is_int/bool` or Python equivalents); real, bitvector or other leaf is an `error` naming it (BV-to-int not supported; documented under Traps). Wide ints read with int64; larger gives `unsupported`/error, stated under Outputs.
- **Optimisation in the runner (decision, differs from the skill's push/pop):** linear tightening on one context with permanent strict atoms (no push/pop), nothing emitted before the proof; timeout before proof gives `timeout` with zero solutions. Each check gets all the remaining time. Pin the optimum for enumeration in a **fresh** context holding the constraints plus `obj == best`. Reason: avoids #616/#433 risk and matches how cvc5_python behaves; the skill's recommended pattern is compatible with it.
- **Enumeration in the runner:** value no-goods over declared output leaves, plus a set of emitted tuples as a second guard (repeats skipped, not counted). Statuses `complete`, `unsat`, `limit`, `timeout` as in the cvc5_python runner.
- Deadline = start + execution_timeout - 0.3 s; outer subprocess timeout stays as backstop.
- Stdout hygiene: protocol on a duplicated fd, fd 1 dup2'd to 2 for the whole run (libyices C-level prints are not caught by `redirect_stdout`).
- Copy readiness_test.py from the closest existing integration (`parents[3]` for the repo root); `metadata.json` readiness_level 2; register pilots (PILOTS, MAXIMIZATION_SWAPS, README); `generate_site.py` entries (`LANGUAGES["c"]=("c","C")`, `EXTENSION_LANGUAGE[".c"]="c"`, `BACKEND_NAMES["yices"]="Yices"`) in the same commit; display names "Yices (C)" and "Yices (Python)".

**yices_c (`solvers/yices/c/`):**
- Files: `metadata.json` (`language c`, `extension .c`, `compilation true`, `framework libyices`, `solver yices`, `paradigms ["smt"]`, `enumeration true`, `readiness_level 2`, no `instance_binding`), `Dockerfile`, `run.py`, `c/dcp.h`, `c/driver.c`, `CONTRACT.md`, `readiness_test.py`, `readiness.json`.
- **How C reads JSON (decision): the harness parses.** `run.py` writes `request.json` to the candidate's stdin; `driver.c` calls `cJSON_Parse` and invokes the submission's `void build(const cJSON *instance);`. cJSON is chosen because it is the library the skill's C example uses, so a standalone-skill model and a Rosetta model use the same reading code. The teachability council's argv path stays only in the skill's JSON example; the contract differs (documented in CONTRACT.md).
- `dcp.h` API: `dcp_set_logic(const char*)` (before any assert), `dcp_assert(term_t)`, `cJSON *dcp_term(term_t)` (output leaf), `dcp_output(name, cJSON*)` (leaf or nested `cJSON_CreateArray`), `dcp_minimize/dcp_maximize(term_t)` at most once, `long dcp_int(const cJSON*)` checked integer read (rejects non-integral or out of range). Numbers over 2^53 lose precision in cJSON: document in CONTRACT.md. Values serialised via `cJSON_CreateRaw("%lld")`.
- Errors: `dcp_assert`/`dcp_term` on `NULL_TERM` or any Yices error after build gives `error` with `yices_error_string()`; driver calls `yices_clear_error()` before build; `dcp::ok`-style helper throws/aborts at the first error to keep the original cause.
- **Runner (decision): own `run.py`, not `runtime.main("cpp")`.** `runtime.cpp_solver` hard-codes `model.cpp` and cmake; changing shared runner code would require recertifying every C++ integration. Reuse `emit`/`finish`. Steps: copy `/input/model.c` to /tmp; `gcc -std=c11 -O2 -I/opt/c -I/opt/yices/include /opt/c/driver.o /tmp/model.c -L/opt/yices/lib -lyices -lcjson -lgmp -lm -o /tmp/candidate` within `compilation_timeout`; nonzero exit gives `compilation_error` with gcc stderr (about 4 KB cut); run candidate with backstop `execution_timeout + 2`; death by signal or nonzero exit without status record gives `error` naming the signal plus the stderr tail.
- Timeout: `setitimer(ITIMER_REAL)` armed before every `yices_check_context`, handler calls `yices_stop_search(cur_ctx)`, disarmed after; INTERRUPTED gives `timeout`.
- Readiness level 2 cases: minimization_step_one, optimization_timeout (Golomb with 3 s, expects `execution_timeout`, zero solutions), auxiliary_free_distinct (solution_limit=3 with a free auxiliary: proves value no-goods), optimum_enumeration (ten optima: proves fresh-context pinning), error_detail (nonlinear product under default context returns Yices's own text; C NULL_TERM from a type mismatch), a C segfault returns `error` naming the signal, stray_stdout (`yices_pp_term(stdout,...)`), plus `compilation_error`. Base on `highs_cpp/readiness_test.py`.

**yices_python (`solvers/yices/python/`):**
- Based on `cvc5_python/run.py` and its readiness test. The runner reads the instance and calls the submission's `build(instance)` returning `(formulas, outputs)` or `(formulas, outputs, (direction, objective))`, plus optional module-level `LOGIC = "QF_NIA"`. Formulas and leaves are Yices term handles (plain Python ints); Python bool/int literals as leaves are rejected with a clear message (use `Terms.integer`). Values read with `Model.get_value`; must be int or bool; `Fraction` is an error. Any exception from build or solving maps to `error` with `str(e)`.
- Timeout: `check_context(timeout=left)` (bindings' Timer thread calling `stop_search`); a SIGALRM `setitimer` backstop only fires between bytecodes, so the container kill is the last resort. Clock checked after each check: UNKNOWN/INTERRUPTED at or past the deadline is `timeout`.
- Stdout: `os.dup2` fd 1 to fd 2 for the run, protocol through the saved fd (small `emit` variant or rebinding `sys.stdout` to the saved fd).
- Readiness: same level 2 cases as C (Python submissions), `stray_stdout` using `print`, `error_detail` with nonlinear arithmetic.

## 7. Probe list (run in the image before writing; results in workspace/probes/)

| ID | Question | Decides |
|---|---|---|
| P0 | Does the source build with MCSAT succeed (libpoly, CUDD)? Is `yices_has_mcsat()` true? Is `-lgmp` needed at link time? | Images, example 8, link line |
| R1 | `assert_formula` after SAT in push-pop mode (C and Python)? after UNSAT? push/pop tightening correct? under QF_NIA/MCSAT? | Optimisation pattern, config line |
| R2 | `get_int64_value` of an output term appearing in no assertion | free-output handling (assert `x == x` or trap) |
| R3 | Python Timer `stop_search` interrupts ctypes `check_context` (GIL released), status INTERRUPTED; reset needed afterwards in push-pop? C SIGALRM likewise | timeout recipes |
| R4 | `stop_search` on a non-searching context: harmless? | race handling |
| R5 | Are errors sticky (does `yices_error_code()` after build still reflect the last failure)? | error handling in driver |
| R6 | `Model.get_value` beyond int64 and 32 bits | wide-value handling |
| R7 | Nonlinear term in default context: error at assert or at check, exact text; QF_NIA with push-pop | error_detail, Common issues |
| R8 | Is a model usable after UNKNOWN? | solving text |
| R9 | `yices` 1.1.6 on Python 3.12 against libyices 2.7.0 (import, version attribute names, init on import) | Python install row |
| R10 | `distinct` with <2 args; `div`/`mod` semantics; Z3-style `x+1` in Python; `new_variable` misuse text; `Terms.and_` | Common issues |
| R11 | Late-pop crash/behaviour (#616) and assumptions (#433) are not exercised, only noted | rationale |
| R12 | BV-to-integer conversion | whether any BV recipe is taught (default: not taught, rejected as output) |

## 8. Order of work

1. Write both Dockerfiles with the shared build stage; build `yices_python` first (smaller), then `yices_c`; run P0 and the other probes.
2. Write the skill from probe results; `check_assets.py` per interface in the images; `skills-ref validate`; `generation.skills validate` and `rosetta-mentions`.
3. Toy rounds (fresh agent per interface; run in the image with `--network none`), fix the skill, round-N results in `workspace/`.
4. Standalone review by a fresh agent; save `solvers/yices/standalone-review.json`.
5. Integrations: `metadata.json`, `run.py`, `dcp.h`/`driver.c`, `CONTRACT.md`, `readiness_test.py`; `check_integration.py ID --static`; `python -m evaluation.build <id>`; `python -m generation.readiness check`; register pilots; `check_integration.py ID` must exit 0.
6. Report and evidence under `generation/runs/20261026-yices-setup/setup/<id>/setup-001/`; record `setup_finished`/`setup_blocked`.

## 9. Known risks carried forward

- Source build time (about 5 to 10 minutes first build; cache shared only if the build stage text is identical).
- Linear tightening may be slow on wide objective ranges: accepted, documented under Solving.
- Bindings classify only Python up to 3.6: tested on 3.12 only; record the tested version.
- Open licence wording (bindings MIT vs PyPI GPLv3): record both, check wheel metadata.
- Agents may carry Z3/cvc5 habits (operator overloading, `Solver().add`, `Optimize`): Common issues and evals must catch them; toy rounds will show.
- Python-ints-as-term-handles ambiguity: contract forbids raw literals as leaves.
