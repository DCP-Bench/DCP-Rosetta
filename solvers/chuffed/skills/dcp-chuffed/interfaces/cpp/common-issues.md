# Chuffed in C++: common issues

Part of the [C++ interface](README.md); concepts in [SKILL.md](../../SKILL.md).

| Problem | Likely cause | Fix |
|---|---|---|
| "invalid new-expression of abstract class type 'X'" | no `print` override: `Problem::print` is pure virtual | override `void print(std::ostream&) override {}`, empty body if unused |
| several solutions printed where one optimum is wanted | `so.print_sol = true` prints each improving solution | [One printed optimum](README.md#all-solutions) |
| "double free or corruption", signal 6 | `vec` copies are shallow: `vec<IntVar*> a = b;` or pushing a local `vec` into a `vec<vec<>>` | build rows in place (`m.push(); m.last().push(x)`); never copy a constraint's argument `vec` |
| "no matching function" on a constraint call | `std::vector`, `{a, b}` or a temporary passed for `vec<...>&` | named `vec` built with `push` |
| `x + y`, `2 * x` do not compile | no expressions | auxiliary `IntVar` + `int_linear` / `int_plus` / `int_times` |
| an `int` where only `IntVar*` is accepted | no implicit constant | `getConstant(k)`, or the `int c` overload |
| `~b` fails | negation of a temporary | `BoolView nb = ~b;` on a named `BoolView` |
| "conversion from 'IntVar*' to non-scalar type 'BoolView'" | `BoolView r = x;`; `vec<IntVar*>` and `vec<BoolView>` do not convert | `BoolView r = newBoolVar(); bool2int(r, x);`, `bool_*` calls for Booleans |
| "cannot convert 'BoolView' to 'Branching*'" | `branch` on `vec<BoolView>` (or on a `vec<vec<>>`) | branch on 0..1 `IntVar`s from `bool2int`; `flatten` a grid first |
| a reported solution breaks a constraint; Booleans read 0 | variables no `branch` reaches stay unfixed (also with `so.vsids`); with no `branch` at all the root is reported | branch on every decision, Booleans through `bool2int`: [globals-tour](../../assets/cpp/globals-tour/README.md); or, after your `branch` calls, `so.vsids = true; engine.branching->add(&sat);` (`<chuffed/core/sat.h>`) to let the SAT search fix the rest |
| `newIntVar(0, 8, true)`: "too many arguments" | `newIntVar` has no eager flag | `IntVar* v; createVar(v, 0, 8, true);` |
| `createVars`/`flatten`/`transpose` misbehave | output `vec` not empty | call once per fresh `vec` |
| abort "arithmetic.cpp:691: Not yet supported" | `int_mod` compiles but is not implemented | `x = q*y + r`, `0 <= r < y` with `int_linear`; parity `x = 2*h + r`, `r` in 0..1 |
| abort "value selection branching is not yet supported" | `VAL_RANDOM` | another `ValBranch`; `so.branch_random` for randomised restarts |
| signal 11 in `lex` | `lex` on rows of eager 0/1 variables | avoid `lex` there |
| no reified form of a global | only linear and binary relations have `_reif` / `_half_reif` | encode with BoolViews and `array_bool_and/or` |
| `int_rel_reif` picks the wrong overload | argument order | `(x, rel, y, r, offset)` with a variable, `(x, rel, c, r)` with a constant: the BoolView comes before the offset |
| element reads the wrong cell or fails | `array_int_element(i, t, y, offset)` reads `t[i - offset]`, default 0; no 2-D form | `offset = 1` for 1-based; keep `i`'s domain inside the table; flatten row-major, `idx = cols*r + c` |
| `inverse` wrong with 1-based values | offsets default to 0 | `inverse(x, y, 1, 0)` etc. (cheat sheet) |
| variable named `and`, `or`, `not` | C++ alternative tokens | rename |
| a large value overflows or is rejected | domains limited to ±500,000,000, 32-bit sums | split into digits or blocks |
| only one solution although more exist | no `output_vars`, or `so.nof_solutions` left at 1 | both, see [All solutions](README.md#all-solutions) |
| nothing printed after `engine.solve`, exit code 0 | root failure calls `exit(0)` | [Solving](README.md#solving), `std::atexit` |
| second `engine.solve` misbehaves | globals cannot be reset | fork or run again |
| program exits on its own arguments | `parseOptions` | parse your arguments yourself |
| undefined references at link time | missing second `chuffed` or Threads | the link line in [Install](README.md#install) |
| infeasible though a solution exists | an auxiliary `IntVar`'s domain too narrow | bound it by the extreme values of its definition |


