# Common issues (ECLiPSe, Prolog)

Back to [the Prolog interface](README.md).

| Symptom | Likely cause | Fix |
|---|---|---|
| `Ambiguous import of alldifferent / 1 from [ic, ic_global] in module eclipse` (twice), then `calling an undefined procedure alldifferent(...) in module eclipse`, `abort` | `ic` and `ic_global` both export it | `:- import alldifferent/1 from ic_global.` |
| `calling an undefined procedure foo_bar(1) in module eclipse` then `abort` | misspelt name, or the library is not loaded (`nth0`/`nth1` need `lib(listut)`, `gcc/2` needs `ic_global_gac`, `table/2` needs `ic_mdd`) | load the library with a directive; an undefined call aborts the whole goal |
| `file m.ecl, line 3: syntax error: postfix/infix operator expected` at `2**70`, `#<=>`, `#\/` or `#/\` | not operators in `ic` or `gfd` | `2^70`, `<=>`, `or`, `and`; or `B #= (X #> 5)` |
| `Gecode exception: IntVar::IntVar: Attempt to create variable with empty domain`, `Error in external function in g_add_newvars_interval(..., 1, 0, 3000000000)` | `gfd` bounds are about 32 bits; `0..3000000000` is too large | keep every bound and product below 2^31, or use `ic` |
| `gfd` `Y #= X*2` with `X :: 0..2000000000` leaves `X` in `0..5000000`, `Y` in `0..10000000`, no error | a variable made by an expression gets a default bound of 10000000 | give the helper variable its domain first |
| `type error in bb_min(labeling([...]), _ + 1, bb_options(...))` | the cost is an expression | `Cost #= Expr`, pass `Cost` |
| `out of range in search([...], 0, input_order, indomain_middle, complete, [])` | `indomain_middle` is not a `gfd` choice | `indomain_min`, `indomain_max`, `indomain_split` |
| output shows `_376519{2 .. 9}` instead of numbers | variable not labelled | `labeling/1` or `search/6` on it |
| `ic` bound reads `1180591620717411172352 .. 1180591620717411565568` | large integers are not exact in `ic` | keep numbers below 2^53 or use `gfd` within its bound |
| `get_var_bounds` prints `4.0 - 9.0` | it returns floats | `get_integer_bounds/3` (`ic`), `get_bounds/3` (`gfd`) |
| `collection_to_list` on a 2-D array returns row arrays; `get_finite_integer_bounds` type error | not flat | `flatten_array/2` |
| `trying to redefine a built-in predicate` for `:- dynamic seed/1` | `seed/1` is built in | pick another name |
| constraints vanish after a loop | failure-driven loop undid them | `( foreach(...) do ... )` |
| `findall` result has unlabelled variables | `findall` copies constraints | label before collecting |
| `Found a solution with cost ...` lines in the output | `bb_min` default reporting | `report_success:true/0, report_failure:true/0` |
| run with a `timeout/3` limit keeps going under `gfd` | the Gecode search is not interrupted | operating-system time limit |
| failure instead of a message | infeasible model, or a wrong constraint that fails | test with `( Goal -> ... ; ... )` |
| `Singleton local variable N in do-loop, maybe param(N) missing?`, then a silent `unsat`, a wrong model, `instantiation fault in +(_, 1, _)` or a hang | an outer variable, an inner loop's outer iterator, or a loop bound is used in the body but not in `param(...)` | add it to `param(...)` of every loop that uses it, or use plain recursion; read the warnings on every run |
| `number expected in set_up_ic_con(7, 1, [0 * 1, -1 * (...), ...])` | a linear expression built at run time (accumulated in a `fromto` loop, or nested through helper terms) was posted through a variable | build a flat list of `Coef*Var` terms and post `Total #= sum(Terms)`, or post one `#=` per term |
| `instantiation fault in mod(_{0 .. 3}, 2, _)` or `number expected in mod(...)`; the same for `//` | `mod` and `//` in `ic` constraints work only when the operand is already a number | write `X #= Q*D + R` with `R :: 0..D-1`, or channel through `element/3` |
| `calling an undefined procedure between(1, 5, _) in module user`, `atom_codes(...)`, `string_to_list(...)`, `append([...], _)` | not available in `lists` or the kernel | `( for(I, 1, N) do ... )` or recursion; `string_list/2` turns a string into character codes; chain `append/3` |
| `Integer or gfd variable expected for: 0.0`, `type error in element(...)` | `floor/1` returns a float | `integer(floor(X))` |
| `type error in indomain(<array>[1,2,2], min)` | `V = X[I,J,P]` does not read an array cell | `V #= X[I,J,P]`, or `V is X[I,J,P]` once fixed |
| `number expected in make_bool(or(and(...)))` | nested `and`/`or` inside an `ic` reification once a part turns ground | 0/1 variables with linear rows: `E #= (A #= B)`, `P #=< E`, `P #>= E + F - 1` |
| `sum/2` ambiguity under `gfd` | `lists` and `gfd` both export it | `H is sum(Ds)` |
| a list element written as `'export'-[...]` parses as `export(-[...])` | the name is a prefix operator | write `-('export', [...])` |
| enumerating all solutions takes far longer than finding one | auxiliary variables are labelled too, so one answer is found once per labelling | make auxiliaries follow from the main variables by propagation instead of labelling them |
| search is slow with plain `labeling/1` | it labels in the order of the list, smallest value first | choose the order with `search/6` (`first_fail`, `input_order`, `smallest`) and the order of the list itself; it often decides between seconds and a timeout |

