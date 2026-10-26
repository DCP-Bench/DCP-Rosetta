# Sources for `yices`

Existing skills: none found; none is used as a source or companion.
The skill stays unpinned.

## Shared (SKILL.md)

- Yices manual, <https://yices.csl.sri.com/doc/> (basic usage, context and model operations, term operations,
  error reports, SMT logics): concepts and the status list.
- Licences: Yices core GPL-3.0 (<https://github.com/SRI-CSL/yices2>, alternative terms offered by SRI); the Python
  binding is MIT in its repository, and PyPI metadata lists GPLv3. Not re-checked inside the wheel.
- Run in both bindings: status numbers (IDLE 0 ... ERROR 6); assert after SAT and after UNSAT accepted; reset after
  interruption; a bound-tightening loop ends in UNSAT and proves the optimum (knapsack 23 in C and in Python, by brute force); no-good enumeration complete (5-queens, 10 solutions)
  while the blocking-clause call stops early; the product of variables rejected in a default context and solved
  under `QF_NIA` (91 = 7 * 13); floor `div`/`mod`; an unconstrained output reads 0 or false; the free-variable
  error for a quantifier variable; a fresh context with `objective == best` enumerates every optimum (10 optimal
  splits in C by an independent itertools count, 30 in Python).

## C

Tested with Yices 2.7.0 (tag `yices-2.7.0`, commit 85cf17e44eac76b5d14b297c09fc9bfecf47ef65) built from source with `--enable-mcsat` against libpoly v0.2.1 and CUDD 3.0.0, gcc 12.2.0, cJSON 1.7.15, Debian bookworm (amd64) in a container. `yices_version` is "2.7.0" and `yices_has_mcsat()` is 1.

Verified by running:

- Header `yices.h` and the manual pages above.
- Link line `cc -std=gnu99 -O2 model.c -o model -lyices`; `-lgmp` is needed only with `<gmp.h>`; JSON examples use
  cJSON 1.7.15 (Debian `libcjson-dev`, MIT).
- the loader error without ldconfig; the segfault when `yices_init()` is skipped; builder error codes 24, 2, 18,
  300, 308, 400, 604; `yices_get_int64_value` on a Boolean fails and leaves the value unchanged; a 1 s SIGALRM calling
  `yices_stop_search` interrupted a hard check at about 1.0 s, then check gives ERROR and `yices_reset_context` gives IDLE.
- Jobshop optimum 8 checked by brute force.
- Not run: the Ubuntu PPA `ppa:sri-csl/formal-methods` named in the install section; the claim that the release
  tarball lacks `libcudd` (from the install documentation, not re-verified).


## Python

Tested with the `yices` 1.1.6 wheel, Python 3.12.11, libyices 2.7.0, Debian bookworm (amd64) in a container.

Verified by running:

- <https://github.com/SRI-CSL/yices2_python_bindings> (README, `yices_api.py` loader, MIT), <https://pypi.org/project/yices/>.
- binding 1.1.6 imports and works against libyices 2.7.0 on Python 3.12; `Yices.version` is a string property;
  terms are Python ints and `x > 3` is a bool; `Terms.and_` does not exist; `Model.from_context` after UNSAT or INTERRUPTED
  does not raise; `get_value` types; `Terms.integer(10**30)` wraps; `check_context(timeout=2)` returned INTERRUPTED at
  about 2.0 s; `pop` without `push` raises the state error; assert after INTERRUPTED raises; the QF_NIA configuration; `one-shot` mode refuses assertions after a check.
- Not run: the Python install block with prefix `/usr/local` and `sudo` (the build used another prefix plus `ldconfig`); the `latest` helper, which resolves to the tested tags `yices-2.7.0`, `v0.2.1` and `cudd-3.0.0` at the time of writing.
- Not run: a model after UNKNOWN (the status was never produced).
