# Python interface build notes (for the shared writer)

Tested: Yices 2.7.0 (source build, `--enable-mcsat`, libpoly v0.2.1, CUDD 3.0.0), `yices` 1.1.6 wheel, Python 3.12.11, Debian bookworm, image `dcp-eval/yices_python:v1`. `yices_api.yices_has_mcsat()` returns 1. Probes: `workspace/probes/python/*.py` (run with `probes/python/run.sh NAME.py`, no network).
Written: `solvers/yices/skills/yices/interfaces/python.md`, `assets/python/<8 examples>`; `check_assets.py --interface python --image dcp-eval/yices_python:v1` gives 8/8. `generation.skills rosetta-mentions` clean. Image: `solvers/yices/python/{Dockerfile,metadata.json}` and a PLACEHOLDER `run.py`.

## Verified facts (each run in the image)
- `from yices import Yices; Yices.version` is a string property ("2.7.0"), not callable. Binding 1.1.6 imports and works against libyices 2.7.0 on Python 3.12. Import initialises Yices; `Yices.exit()` exists, optional.
- Install of binding: `pip install yices` (hash-pinned wheel works). The wheel needs libyices on `find_library('yices')` or `/usr/local/lib` (ldconfig used in image).
- Terms are plain Python ints. `x > 3` is a Python bool: `assert_formula(True)` -> `invalid term: (index = 1)`. `x + 1` silently returns an int (`11`), `x == y` False. No operator overloading.
- Builders: `Terms.add/sub/mul` exactly 2 args; `sum/yand/yor/distinct/xor/product` take a list. `Terms.and_` does not exist. `yand([])`=true, `yor([])`=false, `distinct([x])`=true, `distinct([])` AssertionError, `sum([])`=0.
- Status values: IDLE 0, SEARCHING 1, UNKNOWN 2, SAT 3, UNSAT 4, INTERRUPTED 5, ERROR 6. Plain ints (compare to string is False). `ctx.status()` is a method.
- `Model.from_context(ctx,1)` after UNSAT or INTERRUPTED does NOT raise; values are zeros. (The plan's "from_context raising after UNSAT" is false.) Runner must check the status.
- `get_value`: int for int terms, bool for bool terms, Fraction for real, float for ints beyond int64 (lossy). `get_integer_value` raises `eval error: the term value does not fit the expected type` beyond int64. `Terms.integer(10**30)` silently wraps at int64 (gives 5076944270305263616; `integer(2**63)` = -2**63); `Terms.parse_rational("1000...")` is exact. `Terms.integer(2.5)` and `Terms.integer(term)` return a term silently.
- Unconstrained term: value 0 / false with keep_subst=1; `from_context(ctx,0)` of a term eliminated by substitution raises `eval error: term value not available in the model`.
- `idiv(-7,2)` = -4 (floor); `imod(-7,3)` = 2.
- Default Context() accepts assert after SAT (multi-checks default), assert after UNSAT (silent, status stays UNSAT), and push/pop tightening works. Config modes tested: default/multi-checks/push-pop/interactive all work with assert-after-SAT; `one-shot` raises `operation not supported by the context` at first assert. Assert after INTERRUPTED raises `the context state does not allow operation`; checking again returns ERROR(6); `reset_context()` drops all assertions and gives IDLE. `pop()` without push raises the same state error. pop after UNSAT then check works (SAT).
- Nonlinear: default context raises at `assert_formula(s)` (not at check, not at term construction): `The function yices_assert_formulas failed because: the context does not support non-linear arithmetic`. `Config().default_config_for_logic("QF_NIA")` selects MCSAT; works with tighten loops and push-pop. Logic QF_BV/QF_AX contexts reject arithmetic asserts (`the context does not support arithmetic`), unknown logic `unknown logic`, QF_LIA/QF_IDL/QF_LRA/QF_UFLIA work on linear int problems.
- `check_context(timeout=s)`: returns INTERRUPTED(5) after about s seconds (2.0 s measured for 2), Timer thread cleaned up (thread count 1 after). A hard nonlinear problem under QF_NIA also gives 5 at the limit. `stop_search` on an idle context is harmless (returns None). UNKNOWN (2) was never produced; usability of a model after UNKNOWN NOT tested (do not claim).
- `assert_blocking_clause()` on 3 distinct integer vars (6 solutions) stopped with UNSAT after 1 iteration: incomplete. No-good via `yor(arith_neq_atom)` gives all 6.
- Error text: `new_variable` term asserted: `assertion contains a free variable`; atom with Python number `argument is not an arithmetic term`; Bool+int `argument is not an arithmetic term`; assert int term `type mismatch: invalid argument`; `Types.int_type` uncalled -> ctypes `ArgumentError`; ite with int cond `type mismatch`; `Parameters.set_param` unknown -> `invalid parameter`; dispose then use -> bare `AssertionError`. Duplicate names are allowed silently. Errors are `YicesException` raised at the call.
- Parameters: `Parameters().set_param("random-seed","7")`, `ctx.check_context(params)`.
- Optimisation by tightening with permanent strict atoms worked in default mode and QF_NIA; push/pop tightening gave correct SAT/UNSAT. Minimise/maximise of knapsack verified (optimum 90 / 15).
- Terms are global across contexts; a fresh Context re-asserting `objective == best` enumerates all optima (30 for the partition example).

## Interface table facts (Python column)
Package `yices` (pip, no bundled libyices); operators none (ints); errors raise `YicesException` at the call; values via `Model.from_context(ctx,1).get_value`; time limit `check_context(timeout=)`; big ints: Python ints in `get_value` up to int64, floats beyond, `Terms.integer` wraps (use `parse_rational`); memory `dispose()`; JSON stdlib; start/stop: automatic on import, `Yices.exit()` optional; nonlinear only via a QF_NIA config; no optimiser, no global constraints.

## Sources used
- https://github.com/SRI-CSL/yices2_python_bindings (README, yices_api.py loader behaviour; verified by running), https://yices.csl.sri.com/doc/install-sources.html and install-binaries.html (from research notes; not fetched again), research/python-binding.md. The binary tarball claim (missing libcudd) was NOT re-verified by me (no network on the host/sandbox fetch failed); the skill does not state it. Skill install block uses the same libpoly/CUDD/Yices tags as the Dockerfile but with prefix /usr/local and sudo; the in-image build used prefix /opt/yices (the /usr/local variant was not itself run).
- Licence: not re-checked in the wheel METADATA; the skill says Yices GPL-3.0 (from research notes).

## Handoff for the runner (integration)
- Don't rely on from_context raising. Beware silent int64 wrap in `Terms.integer`; leaves beyond int64 read as float.
- Default modes allow permanent tightening; the pinning context for all optima must be fresh.
