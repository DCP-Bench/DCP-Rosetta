# Yices in Python (yices)

The official ctypes binding of the Yices C library: a thin layer of classes (`Terms`, `Types`, `Context`, `Model`, `Config`) whose methods are the C functions without the `yices_` prefix. The `yices` package does **not** contain the solver; it loads `libyices` at import.
Shared concepts, statuses and enumeration strategy: [SKILL.md](../SKILL.md).

## Install

Install the Yices library first, then the binding:

```bash
# the library, built from source with MCSAT (nonlinear arithmetic); needs gcc, g++, make, cmake, autoconf, automake,
# libtool, gperf, libgmp-dev, git. Prefix /usr/local puts the library where the binding looks first.
latest() { git ls-remote --tags --refs "$1" "$2" | sed 's#.*/##' | sort -V | tail -1; }   # newest release tag
git clone --branch "$(latest https://github.com/SRI-CSL/libpoly.git 'v*')" https://github.com/SRI-CSL/libpoly.git && (cd libpoly && cmake -S . -B build -DCMAKE_INSTALL_PREFIX=/usr/local -DLIBPOLY_BUILD_PYTHON_API=OFF && cmake --build build -j && sudo cmake --install build)
git clone --branch "$(latest https://github.com/ivmai/cudd.git 'cudd-3*')" https://github.com/ivmai/cudd.git && (cd cudd && autoreconf -fi && ./configure --enable-shared && make -j && sudo make install)
git clone --branch "$(latest https://github.com/SRI-CSL/yices2.git 'yices-2.*')" https://github.com/SRI-CSL/yices2.git && (cd yices2 && autoconf && ./configure --enable-mcsat && make -j && sudo make install)
sudo ldconfig
pip install yices
python -c "from yices import Yices; print(Yices.version)"     # a string property, not a call
```

Without `--enable-mcsat` the build is simpler (`./configure && make && sudo make install`) but cannot do nonlinear arithmetic. The Yices page also lists binary archives and packages: [installation](https://yices.csl.sri.com/doc/install-binaries.html), [from source](https://yices.csl.sri.com/doc/install-sources.html). Yices is GPL-3.0; no key or account. If `import yices` raises `Yices dynamic library not found.`, the binding found no `libyices`: it looks up `find_library("yices")` and then `/usr/local/lib`; run `ldconfig` or install to `/usr/local`. The binding's own metadata lists only Python up to 3.6, yet it works on Python 3.12.

## Quick start

```python
from yices import Context, Model, Status, Terms, Types

INT = Types.int_type()
x = Terms.new_uninterpreted_term(INT, "x")          # a decision variable
y = Terms.new_uninterpreted_term(INT, "y")
n = Terms.integer

ctx = Context()
ctx.assert_formulas([Terms.arith_geq_atom(x, n(1)), Terms.arith_leq_atom(x, n(5)),
                     Terms.arith_eq_atom(Terms.add(x, y), n(7)), Terms.arith_gt_atom(y, x)])
if ctx.check_context() == Status.SAT:
    model = Model.from_context(ctx, 1)             # 1 = keep substituted variables
    print(model.get_value(x), model.get_value(y))
    model.dispose()
ctx.dispose()
```

Every term is a plain Python `int` (a handle). Python operators on terms are **not** overloaded: see the traps below.

## Modelling

Binding on [GitHub](https://github.com/SRI-CSL/yices2_python_bindings); the C API in the [manual](https://yices.csl.sri.com/doc/). All builders are static methods of `Terms`, each a thin wrapper of the C function linked in its row; the two-argument ones (`add`, `sub`, `mul`) take exactly two terms, the n-ary ones take one list.

| Need | API |
|---|---|
| integer / Boolean variable | [`Terms.new_uninterpreted_term(Types.int_type(), "x")`](https://yices.csl.sri.com/doc/term-operations.html#c.yices_new_uninterpreted_term), `Types.bool_type()` (also `real_type()`) |
| constants | [`Terms.integer(5)`](https://yices.csl.sri.com/doc/term-operations.html#c.yices_int64) (int64 only), `Terms.parse_rational("100000000000000000000")`, `Terms.true()`, `Terms.false()` |
| bounds, comparison | [`Terms.arith_leq_atom(a, b)`](https://yices.csl.sri.com/doc/term-operations.html#c.yices_arith_leq_atom), `arith_geq_atom`, `arith_lt_atom`, `arith_gt_atom`, `arith_eq_atom`, `arith_neq_atom` |
| sum, difference, scaling | [`Terms.sum([..])`](https://yices.csl.sri.com/doc/term-operations.html#c.yices_sum), `Terms.add(a, b)`, `Terms.sub(a, b)`, `Terms.mul(a, b)`, `Terms.neg(a)`, `Terms.abs(a)` |
| div / mod | [`Terms.idiv(a, b)`](https://yices.csl.sri.com/doc/term-operations.html#c.yices_idiv) floors (`-7 div 2 = -4`), `Terms.imod(a, b)` is non-negative for positive `b` (`-7 mod 3 = 2`) |
| all different | [`Terms.distinct([..])`](https://yices.csl.sri.com/doc/term-operations.html#c.yices_distinct) (one argument gives `true`; an empty list raises `AssertionError`) |
| and / or / not | [`Terms.yand([..])`](https://yices.csl.sri.com/doc/term-operations.html#c.yices_and), `Terms.yor([..])`, `Terms.ynot(t)` (not `and_`); empty `yand` is true, empty `yor` is false |
| implication, equivalence, if-then-else | [`Terms.implies(a, b)`](https://yices.csl.sri.com/doc/term-operations.html#c.yices_implies), `Terms.iff(a, b)`, `Terms.ite(cond, then, else)` (Boolean condition) |
| equality of any sort | [`Terms.eq(a, b)`](https://yices.csl.sri.com/doc/term-operations.html#c.yices_eq), `Terms.neq(a, b)` |
| count / 0-1 value of a Boolean | [`Terms.ite(b, Terms.integer(1), Terms.integer(0))`](https://yices.csl.sri.com/doc/term-operations.html#c.yices_ite), summed |
| element, table, no-overlap, cumulative | no built-in: an `ite` chain, an `yor` of `yand` rows, a pairwise disjunction, a sum of `ite` per time point |
| nonlinear product | [`Terms.mul(a, b)`](https://yices.csl.sri.com/doc/term-operations.html#c.yices_mul) of two variables: needs the `QF_NIA` configuration, see Solving |
| read data from a file | stdlib [`json.loads(Path(p).read_text())`](https://docs.python.org/3/library/json.html); take sizes from the data, ignore unused keys |
| minimise / maximise | no optimiser: tighten `objective < best` (or `>`) in a loop, see All solutions and [SKILL.md](../SKILL.md) |

## Solving

Details: [context operations](https://yices.csl.sri.com/doc/context-operations.html), [model operations](https://yices.csl.sri.com/doc/model-operations.html) (the C functions behind each method).

`ctx.check_context(params=None, timeout=None)` returns an int; compare with `Status`:

| Status | Meaning |
|---|---|
| `Status.SAT` (3) | a model exists; read it |
| `Status.UNSAT` (4) | proven no solution (with a bound added after a solution: the last solution is optimal) |
| `Status.UNKNOWN` (2) | solver gave up, no model |
| `Status.INTERRUPTED` (5) | time limit hit (or `stop_search`), no proof |
| `Status.ERROR` (6) | the context was misused, for example checked again after an interrupt |

- Read values only after `SAT`: `Model.from_context(ctx, 1)` after `UNSAT` or `INTERRUPTED` does **not** raise and returns a model whose values are meaningless (zeros). `model.get_value(t)` gives a Python `int` for integer terms, `bool` for Boolean terms and `Fraction` for reals; `get_bool_value`, `get_integer_value` (int64 only) exist. Integers beyond int64 come back from `get_value` as a lossy `float`; bound the model's integers to the int64 range. Call `model.dispose()`, `ctx.dispose()` when done.
- A term that occurs in no assertion gets the value 0 (or false) with `keep_subst=1`; with `0` the read raises `term value not available in the model`.
- **Time limit**: `ctx.check_context(timeout=seconds)`. It returns `INTERRUPTED` on expiry. The context cannot be used afterwards (asserting raises `the context state does not allow operation`); call `ctx.reset_context()` (it drops all assertions, so assert them again), or start a new `Context`.
- **Nonlinear arithmetic**: the default context is linear and raises when the product is asserted (`the context does not support non-linear arithmetic`). Select a logic: `cfg = Config(); cfg.default_config_for_logic("QF_NIA"); ctx = Context(cfg)` (needs a library built with `--enable-mcsat`; `QF_BV` or `QF_AX` contexts reject arithmetic, an unknown name raises `unknown logic`).
- Search parameters: `p = Parameters(); p.set_param("random-seed", "7"); ctx.check_context(p)`; an unknown name raises `invalid parameter`.
- Errors surface as `YicesException` at the call that fails, with the message of the C function. An assertion after `UNSAT` is accepted silently and the status stays `UNSAT`.
- Terms are global: they outlive contexts, so a second `Context` can assert the same terms again. `Yices.exit()` is optional.

## All solutions

Assert a no-good over the output variables only, then check again; `UNSAT` ends the loop and proves completeness. Do not use `assert_blocking_clause` for integers (see issues).

```python
solutions = []
while ctx.check_context() == Status.SAT:
    model = Model.from_context(ctx, 1)
    values = [model.get_value(t) for t in outputs]          # integer terms
    model.dispose()
    solutions.append(values)
    ctx.assert_formula(Terms.yor([Terms.arith_neq_atom(t, Terms.integer(v)) for t, v in zip(outputs, values)]))
```

Boolean outputs: `Terms.neq(t, Terms.true() if v else Terms.false())`. Optimisation tightens the objective in the same loop; to list all optimal solutions, start a **new** `Context`, assert the same constraints (the terms are reused) plus `objective == best`, and run the loop above ([example](../assets/python/all-optimal-partition/README.md)). Assertions after a `SAT` check are allowed in the default context.

## Common issues

| Problem | Likely cause | Fix |
|---|---|---|
| `assert_formula(x > 3)` raises `invalid term: (index = 1)`; `x + 1` gives a number | terms are Python ints; `x > 3` is a Python bool and `x + 1` adds to the handle | build every expression with `Terms.*` |
| `YicesException ... argument is not an arithmetic term` or `invalid term: (index = N)` | a Python number passed where a term is needed (`Terms.arith_gt_atom(x, 3)`; `Terms.sum([1, 2])` gives the second message, as small ints are read as term handles) | wrap numbers: `Terms.integer(3)` |
| `assertion contains a free variable` | `Terms.new_variable` makes a quantifier-bound variable | use `Terms.new_uninterpreted_term` for decision variables |
| `AttributeError: type object 'Terms' has no attribute 'and_'` / `TypeError: yand() takes 1 positional argument` | Z3-style names or varargs | `Terms.yand([a, b])`, `yor`, `ynot` |
| `check_context() == "sat"` is always false | statuses are ints | compare with `Status.SAT` |
| every value is 0 after infeasible or timed-out run | a model was read without checking the status | read only after `SAT` |
| huge constants silently wrong (`Terms.integer(10**30)` equals `5076944270305263616`) | `Terms.integer` wraps at int64 | `Terms.parse_rational("1000...")` |
| `the context does not support non-linear arithmetic` | product of two variables in a default context | `QF_NIA` config (Solving) |
| enumeration with `ctx.assert_blocking_clause()` reports `UNSAT` after the first solution of 6 | it blocks the Boolean abstraction of the assignment, not the integer values | no-good over the output values |
| `the context state does not allow operation` | assert or check after `INTERRUPTED`, or `ctx.pop()` without a matching `ctx.push()` | `reset_context()` or new context; pair every pop with a push |
| `Yices dynamic library not found.` on import | no `libyices` on the loader path | install it to `/usr/local/lib` and run `ldconfig` |
| `'function' object cannot be interpreted as an integer` | `Types.int_type` passed without calling it | `Types.int_type()` |

## Runnable examples

- [satisfy-magic-square](../assets/python/satisfy-magic-square/README.md): bounds, `distinct`, sums, reading values.
- [all-solutions-queens](../assets/python/all-solutions-queens/README.md): enumerate all with output no-goods.
- [all-optimal-partition](../assets/python/all-optimal-partition/README.md): optimum, then all optimal solutions in a fresh context.
- [maximise-knapsack-json](../assets/python/maximise-knapsack-json/README.md): maximise, data from a JSON file.
- [minimise-colouring](../assets/python/minimise-colouring/README.md): minimise a count of used values.
- [infeasible-pigeonhole](../assets/python/infeasible-pigeonhole/README.md): infeasible as a status.
- [schedule-jobshop](../assets/python/schedule-jobshop/README.md): precedence, no-overlap, makespan, time limit.
- [nonlinear-product](../assets/python/nonlinear-product/README.md): nonlinear integer arithmetic with `QF_NIA`.
