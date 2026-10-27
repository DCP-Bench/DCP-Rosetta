# ECLiPSe in Prolog

ECLiPSe's native interface: models are Prolog files (`.ecl`) run by the `eclipse` launcher.
Shared concepts and outcomes: [SKILL.md](../../SKILL.md). Further pages: [Choosing an encoding](encoding.md), [Common issues](common-issues.md).

## Running

Download a build from [eclipseclp.org](https://eclipseclp.org/) and unpack it. The launcher
is `eclipse`; a plain tarball install can hold only the binary `eclipse.exe`, which needs
`ECLIPSEDIR` (the install directory) and `LD_LIBRARY_PATH` (`$ECLIPSEDIR/lib/x86_64_linux`).
Put it on `PATH` or call it by full path.

```bash
eclipse.exe -f model.ecl -e main            # load model.ecl, run the goal main/0, then stay in the toplevel
eclipse.exe -f model.ecl -e main -- a.json  # user arguments after --
```

With stdin at end-of-file (`</dev/null`) the toplevel ends after the goal. Put `halt` at the end
of `main` or redirect stdin. Exit codes are unreliable: read the output.
`argv(all, L)` inside the goal gives `[ProgramPath | UserArguments]` as strings.

```prolog
:- lib(ic).                       % directives run while the file loads
main :- X :: 1..9, X #> 3, X #< 6, labeling([X]), writeln(X).   % prints 4
```

A model is a file of clauses; `main/0` is the entry. Variables start with an upper-case letter
or `_`. Strings use double quotes; `printf("%d %w%n", [N, Term])` prints (`%d` integer, `%w` any
term, `%n` newline). Call `lib/1` as a directive, never inside a clause body (the operators
it adds must exist when the clauses are read).

## Libraries

| Library | Gives |
|---|---|
| `ic` | integer and real interval constraints `#=`, `#\=`, `#<`, `#=<`, `#>`, `#>=`, `$=`; `::`, `labeling/1`, `indomain/1`, `search/6`; `alldifferent/1`, `element/3`, `circuit/1`; `sum/1`, `min/max` |
| `ic_global` | `alldifferent/1`, `atmost/3`, `occurrences/3`, `lex_le/2`, `sorted/2`; also exported, not run here: `alldistinct/1`, `ordered/2`, `nvalue/2`, `bin_packing/3`, `alldifferent_matrix/1` |
| `ic_mdd` | `table/2` for `ic` (also re-exported by `ic_global_gac`) |
| `ic_global_gac` | `gcc/2` and other GAC versions of the globals |
| `ic_edge_finder`, `ic_edge_finder3` | `disjunctive/2`, `cumulative/4`: the strongest propagation for scheduling |
| `ic_cumulative`, `cumulative` | `cumulative/4` with weaker propagation |
| `gfd` | the Gecode solver, replaces `ic`: `::`, `#=` and the globals `alldifferent/1`, `gcc/2`, `table/2`, `cumulative/4`, `disjunctive/2`, `circuit/1`, `element/3`, `regular/2`, `count/4`, `bin_packing/3`; integers within about 32 bits |
| `branch_and_bound` | `bb_min/3`, `minimize/2` |
| `listut` | `nth0/3`, `nth1/3` and more list predicates |
| `timeout` | `timeout/3` |
| `json` | `json_read/3`, `json_write/3` |
| `ic_sets`, `fd` | set variables; the older `fd` solver (`:: ` plus `#=`). Not used in this skill |

The programs here load either `ic` or `gfd`. Loading `ic` and `ic_global` together makes
`alldifferent/1` ambiguous. Resolve it with the import below; the same import works for any
name both libraries export.

```prolog
:- lib(ic).
:- lib(ic_global).
:- import alldifferent/1 from ic_global.
```

Under `gfd`, `gcc/2`, `table/2`, `cumulative/4`, `disjunctive/2` and `circuit/1` are part of `gfd`
itself; do not load `ic_global` there.

## Modelling

Docs: [ic library](https://eclipseclp.org/doc/bips/lib/ic/index.html), [gfd library](https://eclipseclp.org/doc/bips/lib/gfd/index.html).

| Need | Syntax |
|---|---|
| domain of one variable | `X :: 1..9`, or a list `[1,3,5]` for chosen values |
| the same domain on a list | `Xs :: 0..1` |
| list of fresh variables | `length(Xs, N), Xs :: 1..N` |
| array | `dim(M, [N,N]), M[1..N,1..N] :: 1..NN`; cell `X is M[I,J]` |
| array to list | `flatten_array(M, Flat)` (all cells); `collection_to_list(M[I,1..N], Row)` (one row); on a whole 2-D array it gives a list of row arrays |
| arithmetic | `X #= Y + 2*Z`, `X #\= Y`, `X #< Y`, `#=<`, `#>`, `#>=`; operators `+ - * // mod abs min max`, `sum(List)`, `max(List)`, `min(List)`, `^` |
| reals | `X $= 3 / 2` gives the interval `1.5__1.5`; `X :: 0.0..10.0, X * 2 $= 7` gives `3.5__3.5` (`ic` only) |
| loop over a list | `( foreach(X, Xs) do Goal )`; two lists in step: `( foreach(X, Xs), foreach(Y, Ys) do ... )` |
| build a list in a loop | `( foreach(X, Xs), foreach(T, Ts) do T = W*X )`: the second `foreach` is the output |
| integer loop | `( for(I, 1, N) do ... )`, `count(I, 1, _)`, nested `multifor([I,J], 1, [N,M])` |
| accumulate | `( foreach(X, Xs), fromto(0, A, B, Total) do B is A + X )` |
| outer variables in a loop | list every variable the body shares with the clause in `param(V1, V2)`. This holds for every loop, an inner `foreach` inside an outer one, and a loop bound such as `for(I, 1, D)`. A variable left out is silently a fresh variable in each iteration, so the constraint does nothing; the only sign is the warning `Singleton local variable I in do-loop, maybe param(I) missing?` |
| reification | `B #= (X #> 5)`, or `(X #> 5) => (Y #> 3)`, `<=>`, `or`, `and`, `neg` |
| value of a fixed variable | `Y is X + 1` works only once `X` is a number; use `#=` while `X` is open |

Constraints posted inside a `do` loop stay. A failure-driven loop (`member(...), post, fail`)
undoes everything it posted.

`#<=>`, `#\/` and `#/\` are not operators in `ic` or `gfd` (syntax error). Use `<=>`, `or`, `and`, `neg`,
`=>`. `**` is not an operator either: write `2^70`. In `ic`, `2^70` gives a bound interval
`1180591620717411172352 .. 1180591620717411565568`, not an exact integer: `ic` keeps bounds as
floats beyond 2^53, so large products are not exact.

Reading a domain: `get_var_bounds(X, Lo, Hi)` returns floats in `ic` (`4.0 - 9.0`);
`get_integer_bounds(X, Lo, Hi)` in `ic` and `get_bounds(X, Lo, Hi)` in `gfd` return integers (`4 - 9`);
`get_domain_as_list(X, L)` gives `[4,5,6,7,8,9]`. A variable that was not labelled prints as
`_123{2 .. 9}`.

## Global constraints

Every name and arity below was run.

| Constraint | Call | Library |
|---|---|---|
| all different | `alldifferent(Xs)` | `ic`, `ic_global`, `gfd` |
| element, 1-based | `element(I, List, V)` | `ic`, `gfd` |
| occurrences, at most | `occurrences(Val, Xs, N)`, `atmost(N, Xs, Val)` | `ic_global` |
| global cardinality | `gcc([gcc(Lo,Hi,Val), ...], Xs)` | `ic_global_gac`; in `gfd` the specs are `gcc{low:Lo,high:Hi,value:Val}` |
| table | `table([[A,B]], Rows)` (list of variable tuples, list of allowed rows) | `ic_mdd`; in `gfd` `table(Vars, Rows)` takes one flat tuple `[A,B]` |
| cumulative | `cumulative(Starts, Durations, Demands, Limit)` | `ic_edge_finder`, `ic_cumulative`, `gfd` |
| no overlap | `disjunctive(Starts, Durations)` | `ic_edge_finder`, `gfd` |
| circuit | `circuit(Succ)`: one cycle over all, 1-based successors | `ic`, `gfd` |
| lexicographic | `lex_le(Xs, Ys)` | `ic_global` |
| sorted | `sorted(Xs, Ys)` | `ic_global` |

`circuit/1` demands one cycle through every variable (checked in `ic`: `circuit([1,3,2])` with a self loop and
`circuit([2,1,3])` with two cycles both fail), so it cannot skip a node; a route that visits only some nodes
needs another encoding. `element/3` indexes from 1.

## Search

`labeling(Xs)` tries variables in order, smallest value first. `indomain(X)` labels one variable.
`search(Vars, Arg, Select, Choice, Method, Options)` in `ic` and `gfd` chooses the order:

| Argument | Values used |
|---|---|
| `Arg` | `0` for a list of plain variables |
| `Select` | run: `input_order`, `first_fail` (smallest domain), `anti_first_fail`, `smallest` (smallest lower bound). Documented, not run: `largest`, `occurrence`, `most_constrained`, `max_regret` |
| `Choice` | run: `indomain_min`, `indomain_max`, `indomain_split`. Documented, not run: `indomain_median`, `indomain_random`. `indomain_middle` fails in `gfd` |
| `Method` | `complete` for the full tree; limited-discrepancy and bounded-backtrack methods exist |

Effect on speed is in [Choosing an encoding](encoding.md). Pick `first_fail` for
puzzles and `smallest` with `indomain_min` for scheduling start times, and measure.

## Optimisation

`bb_min(Goal, Cost, Options)` in `lib(branch_and_bound)` finds a solution of `Goal`, then
restarts or continues with a tighter bound on `Cost` until none exists. `Cost` must be a
**variable** (`type error in bb_min(...)` for an expression such as `X+1`): post `Cost #= Expr` first.
Maximise by minimising a negated variable. When `bb_min` exits normally the variables hold the
best solution and the optimum is proven, unless `timeout` was set in the options.

```prolog
:- lib(ic).
:- lib(branch_and_bound).
main :-
    X :: 0..10, Y :: 0..10, X + 2*Y #=< 14, Cost #= -(3*X + 2*Y),
    bb_min(search([X,Y], 0, input_order, indomain_max, complete, []), Cost,
           bb_options{report_success:true/0, report_failure:true/0}),
    printf("%d %d %d%n", [X, Y, Cost]).
```

| Option | Effect |
|---|---|
| `report_success:true/0`, `report_failure:true/0` | silence the `Found a solution with cost ...` lines that go to stdout by default |
| `strategy:continue` (default), `restart`, `step`, `dichotomic` | how the bound moves; `dichotomic` bisects the cost range. Equal speed on the 7x7 job shop measured below |
| `delta:D` | a new solution must improve by at least `D` (default 1.0); use a smaller value for fractional costs |
| `timeout:Secs` | stop after that time, exit normally with the best found, print `Branch-and-bound timeout while searching for solution better than N`; the optimum is not proven |
| `solutions:all` | backtrack through every optimal solution |
| `report_timeout:mark/0` | hook so the model can record that the run was cut |

To tell a proven optimum from a cut run, set `timeout` together with a `report_timeout` hook that sets
a flag, or run the search under an external time limit. `minimize/2` is the short form; it was not run here.

## All solutions

```prolog
findall(Xs, ( model(Xs), labeling(Xs) ), All)    % label only the decision variables; copies are ground
```

Label inside the goal: `findall` copies the variable and its constraints. For all optimal
solutions use `bb_options{solutions:all}` inside `findall`, or find the optimum first and
enumerate under `Cost #= Opt`. `once(Goal)` keeps the first solution. Examples:
[all-solutions-queens](../../assets/prolog/all-solutions-queens/README.md), [all-optimal-team](../../assets/prolog/all-optimal-team/README.md).

## Timeouts

`lib(timeout)`: `timeout(Goal, Seconds, TimeoutGoal)` runs `TimeoutGoal` when the time is up.
With `ic` a 2 s limit on a 40-queens `labeling` stopped as expected. With `gfd` a 100-queens
`search/6` wrapped in `timeout/3` with a 2 s limit was still running after more than 2 minutes
(the Gecode search is not interrupted; a magic-square N=6 run ignored a 60 s limit the same way).
**With `gfd`, impose the limit from outside** (an operating-system `timeout` on the process).
For `bb_min` use the `timeout` option.

## Reading data and printing

```prolog
:- lib(json).
% excerpt of the data-assignment example
read_rows(Rows) :- open("data.json", read, S), json_read(S, {Members}, [names_as_atoms]), close(S),
                   memberchk(cost:Rows, Members).
% ... and at the end of main:
%   printf("total %d, task %w\n", [T, Task]).
```

`json_read/3` with `names_as_atoms` returns an object as `{[key:Value, ...]}`, arrays as lists,
strings as strings. Unused keys are ignored with `memberchk`. `json_write/3` (with `indent(0)` for one line) writes JSON.
Example: [data-assignment](../../assets/prolog/data-assignment/README.md). `gfd` prints `Loaded Gecode solver 6.2.0`
on stdout at first use.

## Examples

Each folder holds `model.ecl` and a README with the command and measured time. All run in about 0.3 s wall.

| Example | Pattern | Run |
|---|---|---|
| [satisfy-magic-square](../../assets/prolog/satisfy-magic-square/README.md) | arrays, `alldifferent`, sums | `eclipse.exe -f model.ecl -e main` |
| [all-solutions-queens](../../assets/prolog/all-solutions-queens/README.md) | `findall`, decomposed queens | same |
| [maximise-knapsack](../../assets/prolog/maximise-knapsack/README.md) | `bb_min` with a negated value | same |
| [minimise-jobshop](../../assets/prolog/minimise-jobshop/README.md) | `disjunctive/2`, minimise | same |
| [cumulative-schedule](../../assets/prolog/cumulative-schedule/README.md) | `cumulative/4`, minimise | same |
| [table-element-lex](../../assets/prolog/table-element-lex/README.md) | `table/2`, `element/3`, `lex_le/2`, `sorted/2` | same |
| [routing-tour](../../assets/prolog/routing-tour/README.md) | `circuit/1`, `element/3` | same |
| [infeasible-pigeonhole](../../assets/prolog/infeasible-pigeonhole/README.md) | infeasible | same |
| [data-assignment](../../assets/prolog/data-assignment/README.md) | JSON input and output | same, `-- other.json` for another file |
| [all-optimal-team](../../assets/prolog/all-optimal-team/README.md) | all optimal solutions | same |

Docs: [ECLiPSe documentation](https://eclipseclp.org/doc/), [library index](https://eclipseclp.org/doc/bips/lib/index.html).
