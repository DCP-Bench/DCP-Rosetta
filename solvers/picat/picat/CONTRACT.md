# picat: how this integration realises the submission contract

Read [the submission contract](../../CONTRACT.md) first; this file only says how Picat
expresses it. Runner: [run.py](run.py), which writes the instance as a Picat term and
starts the driver [driver.pi](driver.pi) in a separate `picat` process. The driver loads
the submission, calls `model/4`, owns search, optimisation and enumeration, and writes
the protocol records to a file, never to stdout.

## Submission file

One Picat file, `model.pi`. It must **import exactly one solver module, `cp` or `sat`**;
the driver solves with whichever one is loaded. Other library modules (`import util.`)
are fine. No other file of yours is staged.

## Entrypoint

```picat
model(Data, Vars, Outputs, Options) => ...
```

The driver calls `model/4` with `Data` bound and the other three unbound, once to prove
the optimum and once more to enumerate (the model is rebuilt from scratch each time).
`Vars` is the decision variables to label (a list, array, or nested lists/arrays). The
driver labels every variable in `Vars` first, in that order, then any still free in
`Outputs` or the objective; under `cp` it finally labels whatever remains in suspended
constraints (`solve_suspended`). A `model/4` that fails is reported as `unsat`. A standalone model also defines
`main/1` over one file name (see [Standalone run](#standalone-run)); the driver never calls it, since its own
`main/1` takes the request and record files.

## Instance

`Data` is a Picat **map**. Keys are atoms: `Data.get(n)`, and `Data.get('N')` or
`Data.get('_SHIP')` with quotes for a name starting with a capital or underscore. Values:

- integers as integers, floats as floats;
- JSON `true` / `false` as **`1` / `0`** (Picat has no Boolean type);
- strings as Picat strings (lists of one-character atoms); a string holding a control
  character other than newline or tab is refused (`error`);
- arrays as **lists, indexed from 1** (`Grid[2,1]` is row 2, column 1 of a list of
  lists); ragged lists are fine;
- nested objects as maps, `null` as the atom `null`.

## Outputs

`Outputs` is a **nonempty list of `Name = Value`** pairs (or a map), one per declared
output. `Name` is an atom (`'A' = Xs` for a capital) or a nonempty string. `Value` is an
integer, a domain variable, or a list or array of these nested to the declared shape; a
2-D array from `new_array(R, C)` is written as a list of rows. A value still unbound after
labelling is an `error`. A declared Boolean is an integer `0`/`1`; an atom, string or
float is serialised (as a JSON string or float) but then rejected by the evaluator. The
driver drops a solution whose output object repeats one already reported.

## Objective

Put at most one objective in `Options`, written with `$`: `$min(Obj)` or `$max(Obj)`,
where `Obj` is a variable or an expression (the driver ties an expression to a fresh
variable with `#=`). Everything else in `Options` (e.g. `ff`, `split`) is passed to
`solve/2`; `Options` must be a list, `[]` for satisfaction.

State the problem's own objective, in the brief's direction. The driver reports the value of its
objective variable (equal to `Obj`; `cp` and `sat` optimise it in the stated direction) as each
solution's `objective`, and the same variable's value at each `$report` as an incumbent.

## Solving

- The driver adds no search options of its own: it calls `solve(Options, LabelVars)` of
  the imported module (`cp` or `sat`) with the submission's `Options`, plus the
  objective option and a `$report` in the first phase. Under `cp` it then runs
  `once(solve_suspended([]))` on each solution.
- Optimum phase: `once(solve([$min(V), $report(...)|Options], LabelVars))`; both modules
  return the first solution only once it is proven optimal. Failure there is `unsat`.
  The `$report` goal (a callback that leaves the search as it is) records each improving
  solution's objective as an `incumbent`, with the seconds since that `solve` call;
  `run.py` relays these while the driver runs. A submission's own `$report` in `Options`
  replaces it, and no incumbents are reported.
- Enumeration phase: the model is rebuilt, `V #= Optimum` is posted, and the driver
  backtracks into `solve/2` for the next labelling of `LabelVars`; nothing else is added.
  A solution whose output object repeats one already reported is dropped. It stops at
  `limit` once enough distinct ones are out; when backtracking fails the search is
  exhausted: `complete` after a solution, `unsat` for a satisfaction model with none (an
  optimum not found again is `error`).
- The time budget: `run.py` kills the `picat` process at `execution_timeout` less 1 s
  (and less the time it spent before starting it), keeps the solutions recorded so far,
  and reports `timeout`. A `picat` exit without a status record is `error`.

## Compilation

No separate step. The driver compiles the file with `cl/1` at run time, inside the
execution budget (`execution_timeout`, less a 1 s margin); `compilation_timeout` does not
apply. A syntax error is an `error` whose detail carries Picat's own message with the
line range.

## Environment

Image `dcp-eval/picat:v1`: the official Picat 3.9#12 64-bit Linux build (checksummed),
driven from Python 3.12.11 (standard library only). The binary is
`/opt/picat/picat` and is **not on `PATH`**; its library modules are in
`/opt/picat/lib` (`cp`, `sat`, `util`, `planner`, `ordset`, `datetime`, `math`, `os`,
...). Solver modules `cp` and `sat` are usable; `mip` and `smt` are present as modules
but have no external solver installed. Picat has no JSON library; a submission needs
none, because the instance arrives as a map and the driver writes the JSON. No
environment variables are set for Picat. The evaluator runs the container with no
network, a read-only root file system, user 65534, `HOME=/tmp`, a 512 MiB writable
`/tmp` and `/input` read-only. For an ad hoc run, override the entrypoint: `docker run
--rm --network none --entrypoint sh dcp-eval/picat:v1 -c '/opt/picat/picat ...'`.

## Traps

- **`Data.get(key)` can return a wrong value for a key named like a built-in** (`length` in Picat 3.9): use the
  three-argument `get(Data, length, Default)`. A key starting with a capital or underscore is quoted, `Data.get('N')`.
- **Indices**: `X[I,J]`, never `X[I][J]` (a syntax error); an index that is a decision variable needs `element/3` in
  `cp`. A `table_in` tuple is `{A,B}`, not `(A,B)` or a list.
- A model with a slow search runs the same in a reader's `picat model.pi data.dat` as in the evaluator: give it a
  finite domain per variable and a global constraint (`all_different`, `circuit`, ...) rather than pairwise `#!=`.

- **Import exactly one of `cp` and `sat`.** Neither, both, `mip` or `smt` is an `error`
  before any solving.
- **Write `$min(...)` / `$max(...)`**: without `$`, Picat calls the `min`/`max` function
  instead of building the option term. More than one objective option is an `error`.
- **Keep `model/4` deterministic**: define it with `=>`, not `?=>`, and leave no choice
  points in its body (a generating `member/2`, say). Enumeration backtracks through
  `solve/2` and then into `model/4`, and would report solutions of a second, different
  model.
- **`model/4` must give the same model on both calls**: no global state or randomness.
- Avoid predicate names starting with `dcp_`, and do not define `main/1`: the
  submission is loaded into the driver's program.
- Printing (`println`) is harmless but useless: stdout is relayed to stderr as a log.

## Standalone run

A model is also a file a person downloads and runs on its own, so it opens with a header comment: the problem
statement, where the data comes from and the commands that run it. The data is converted by
[dcp_convert_picat.py](dcp_convert_picat.py), the same file the runner imports, which the model's page offers beside
the instances: it writes `<problem>_1.dat`, `<problem>_2.dat`, ... (one Picat term per instance), and the model ends
with a run block that reads one, builds `Data` as a map, calls `model/4`, solves and prints the outputs:

```picat
% <problem>: a Picat model from DCP Rosetta.
%
% <the problem statement, as below>
%
% Save this file as model.pi. Download `<problem>.json` and `dcp_convert_picat.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/<problem>.html
% Convert the instances once, then run the first one (Picat 3.9, https://picat-lang.org):
%   python dcp_convert_picat.py <problem>.json
%   picat model.pi <problem>_1.dat
```

```picat
% Reads the data file, builds the model, solves it and prints each output.
main([File]) =>
    Fd = open(File),
    Term = read_term(Fd),
    Term = $json_object(Keys, Values),
    close(Fd),
    Data = new_map([K = V : {K, V} in zip(Keys, Values)]),
    model(Data, Vars, Outputs, Options),
    solve(Options, Vars),
    solve(vars(Outputs)),
    foreach(Name = Value in Outputs)
        printf("%w = %w\n", Name, Value)
    end.
```

`solve(Options, Vars)` labels `Vars` and optimises the `$min`/`$max` in `Options`, as the driver does, and
`solve(vars(Outputs))` labels an output variable that is not in `Vars`. **A problem with no instance data** (the
instance is `{}`) has a shorter header with no download or convert line, `picat model.pi` to run it, and a run block
`main =>` (Picat calls `main/0` when no argument is given) that calls `model(new_map(), Vars, Outputs, Options)`:

```picat
% <problem>: a Picat model from DCP Rosetta.
%
% <the problem statement>
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/<problem>.html
% Save this model as model.pi and run it (Picat 3.9, https://picat-lang.org) with:
%   picat model.pi
```

The problem statement is the description's own words or a faithful short paraphrase of them (never a narrowing: "any
two landings", not "consecutive landings"), no longer than needed: no instruction about printing and no remark about
the instance. A comment after the header says what each field the model reads holds (`Data.get(values)`: the value
of each item, a list indexed from 1), since the data is a map, not declared parameters. The run block is the same in
every model apart from the no-data form.

## Example

The pilot fixture [tests/fixtures/model_picat.pi](../../../tests/fixtures/model_picat.pi)
(instance fields `n`, `optimize` (arriving as `1`/`0`); outputs `x`, `y`):

```picat
import cp.

model(Data, Vars, Outputs, Options) =>
    N = Data.get(n),
    [X, Y] :: 0..N,
    if Data.get(optimize) == 1 then
        X + Y #>= N,
        Options = [$min(X + Y)]
    else
        X + Y #= N,
        Options = []
    end,
    Vars = [X, Y],
    Outputs = [x = X, y = Y].
```
