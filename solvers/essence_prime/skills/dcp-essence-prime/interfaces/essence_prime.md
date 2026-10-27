# Essence' with Savile Row and Minion (Essence' text)

Savile Row reads a `.eprime` model plus a `.param` file and runs Minion on it from the command line. Shared concepts, modelling rules, pitfalls and search advice: [SKILL.md](../SKILL.md); language reference: [language.md](../references/essence_prime/language.md).

## Install

```bash
curl -fLO https://www-users.york.ac.uk/peter.nightingale/savilerow/savilerow-1.11.1-linux.tgz
mkdir savilerow && tar -xzf savilerow-1.11.1-linux.tgz -C savilerow --strip-components=1
export PATH="$PWD/savilerow:$PATH"          # the `savilerow` launcher script; Minion is in savilerow/bin/
java -version && savilerow -help | head -1  # "Savile Row 1.11.1 ..."
```

If the launcher's directory is not on `PATH` (a container image that unpacks the tarball elsewhere, for instance), the bare `savilerow` command is `not found`: run `DIR/savilerow` with its full path, or put `DIR` on `PATH`. The commands below use the bare name.

The tarball bundles Minion (plus Chuffed and Kissat for other back ends). The `savilerow` script runs `java -Xmx8G -jar savilerow.jar` and passes `-minion-bin bin/minion` itself; on a smaller machine call the jar directly with a lower heap: `java -Xmx2g -Djava.library.path=DIR/lib -jar DIR/savilerow.jar model.eprime p.param -run-solver -minion-bin DIR/bin/minion`. Releases and macOS builds: [Savile Row releases](https://www-users.york.ac.uk/peter.nightingale/savilerow/releases.html).

## Quick start

```bash
cat > hello.eprime <<'EOF'
language ESSENCE' 1.0
$ n distinct values from 1..n, the first larger than the last
given n : int(1..10)
find x : matrix indexed by [int(1..n)] of int(1..n)
such that
allDiff(x),
x[1] > x[n]
EOF
printf "language ESSENCE' 1.0\nletting n = 4\n" > hello.param
savilerow hello.eprime hello.param -run-solver -solutions-to-stdout   # prints: letting x be [2, 3, 4, 1]
savilerow hello.eprime -params "letting n = 4" -run-solver            # inline data; writes hello.eprime.solution
```

## File shape

```
language ESSENCE' 1.0
$ one-line statement of the problem
given n : int(1..20)                          $ parameters, values come from the .param file
letting c = 5                                 $ named constants
find q : matrix indexed by [int(1..n)] of int(1..n)   $ decision variables
branching on [q]
such that
$ a comment line per constraint block
allDiff(q),
forAll i : int(1..n) . q[i] != c
```

- Header `language ESSENCE' 1.0` (ASCII apostrophe). Comments start with `$`.
- Order: header, `given`, `letting`, `find`, `where`, `branching on`, `heuristic`, objective, `such that`. Verified: `branching on` or `heuristic` after `minimising` is a parse error. Constraints are separated by commas; **no trailing comma**, and one `such that`.
- Parameter file: the header plus one `letting n = 6` per `given` (ints, `true`/`false`, matrix literals `[[1,2],[3,4]]`); order does not matter, so a size may come after the matrix it sizes. A matrix literal is rectangular and has exactly as many entries as the declared index domain, else `Index domains do not match for the matrix F`.
- Every `find` needs a finite domain: `int(lo..hi)`, `bool`, or `matrix indexed by [D1, D2] of Base`. Matrices are 1-based by default.
- Full syntax, operators and globals: [references/language.md](../references/essence_prime/language.md).

## Run and read results

```
savilerow model.eprime data.param -run-solver                    # one solution, or the optimum
savilerow model.eprime data.param -run-solver -all-solutions -S0 # enumerate (satisfaction only)
savilerow model.eprime data.param -run-solver -num-solutions 5 -S0
```

Options: [manual section 4.5](https://arxiv.org/abs/2201.03472), `savilerow -help`.

- **Where results go.** By default `<param>.solution` (or `<param>.solution.000001`, ... for several), `<param>.info`, `<param>.minion`; with no param file the prefix is the model name. `-solutions-to-stdout` prints them instead, separated by `----------`; `-out-solution`, `-out-info` rename the files. Run in a writable directory: Minion also writes hidden temp files there.
- **Solution text**: `language ESSENCE' 1.0`, `$` info lines (nodes, time, `SolverTimeOut`), then `letting NAME be VALUE` per `find`, in alphabetical order: ints `5`, bools `true`, matrices `[1, 2, 3]`, 2-D as nested rows over several lines; a matrix not indexed from 1 carries its domain, `[1, 2, 3;int(0..2)]`. A parser is in [the JSON example](../assets/essence_prime/json-input/solve.py). `-mode ReadSolution` and `-param-to-json` convert files.
- **Status lives in the info file** (`<param>.info`), not in the exit code:

| Info line | Meaning |
|---|---|
| `SolverSatisfiable:1` | a solution was written |
| `SolverSatisfiable:0` + `SolverTimeOut:0` | proven infeasible: exit code 0, no solution file, nothing on stdout ([example](../assets/essence_prime/pigeonhole/README.md)) |
| `SolverTimeOut:0` | Minion finished: an optimum written is **proven**, an enumeration is complete |
| `SolverTimeOut:1` | Minion hit its limit: the solution written is the best found, **not** proven optimal |
| `SavileRowTimeOut:1` | Savile Row ran out of time before Minion started |

- **Time limits**: `-timelimit S` limits Savile Row's translation only; once Minion runs it is not stopped (measured: a Golomb-ruler run with `-timelimit 2` ran Minion for 100 s). Cap Minion with `-solver-options "-cpulimit S"`; give both.
- **Errors** print `ERROR: ...` and exit nonzero; parse errors name the line and column. Some warnings are harmless and do not change the exit code: `Number of givens in model file does not match number of lettings` (the param file sets other names too), `interval 1..0 is out of order`, and, for an **empty** matrix (`letting edges = []` where the domain is `int(1..0)`), `Index domains do not match for the matrix edges`. An empty matrix gives exit 0 and a correct solution with those warnings on stderr. The `-all-solutions` warning recommending `-S0` is not harmless: see below.

## Objective and enumeration

`minimising EXPR` or `maximising EXPR`, one per model, on its own line, after any `branching on`/`heuristic` and before `such that`. EXPR is an int expression (a variable or a sum). Only the best solution is written, and only after the search finished or hit its limit; `-all-solutions` and `-num-solutions` are ignored with a warning on an optimisation model.

- **Pass `-S0` when enumerating.** The default `-S1` lets Savile Row delete "unused" `find` variables by fixing them to one value, and a variable whose only constraints are unary counts as unused (they fold into its domain). Measured: `find x : int(1..3)` with `x != 2` gives 1 solution under `-S1`, 2 under `-S0`; an unconstrained `find` is likewise pinned. With `-S0`, every `find` is enumerated, so a free auxiliary variable repeats each solution once per value: pin it to a function of the others or leave it out.
- **All optimal solutions**: solve, check `SolverTimeOut:0`, read the optimum, then re-solve **without** the objective line and with `(EXPR) = optimum` appended after the last constraint, using `-all-solutions -S0` ([example](../assets/essence_prime/all-optimal/README.md)). Parenthesise EXPR: `sum i : D . e = v` would put `= v` inside the sum. To read the optimum of an expression, add `find best` with `maximising best` and `best = (EXPR)`. That wrapper is needed only for an expression objective: when the objective is already one variable (`maximising total`), read it directly and fix it in pass 2 (`total = optimum`), which enumerates the same solutions.

## Common issues

| Symptom | Cause | Fix |
|---|---|---|
| `Index domains do not match for the matrix F` | param matrix size differs from the `given` domain (an error when F is not empty) | size it from a `given` ([Modelling rules](../SKILL.md#modelling-rules)). An empty `F = []` for a `int(1..0)` domain is only a warning: exit 0, correct solution ([Run](#run-and-read-results)) |
| `savilerow: not found` | launcher directory not on `PATH` | run it by full path or add its directory to `PATH` ([Install](#install)) |
| `-all-solutions` lists too few solutions | default `-S1` fixed a variable | add `-S0` ([enumeration](#objective-and-enumeration)) |
| `-all-solutions` repeats the same values | a free auxiliary `find` under `-S0` | pin it or remove it |
| optimisation returns one solution only | expected: enumeration is ignored there | [all optimal](../assets/essence_prime/all-optimal/README.md) pattern |
| no solution file, exit 0 | infeasible, or a limit hit | read `SolverSatisfiable` / `SolverTimeOut` in `.info` |
| run goes past `-timelimit` | that limit stops Savile Row only | add `-solver-options "-cpulimit S"` |
