# Picat (cp and sat)

The one binding: Picat programs run with the `picat` executable. What holds in every interface (concepts, outcomes, enumeration strategy, solver-level issues) is in [SKILL.md](../SKILL.md).

## Contents
- [Install](#install)
- [Quick start](#quick-start)
- Modelling: [SKILL.md](../SKILL.md#modelling)
- [Solving](#solving)
- [All solutions](#all-solutions)
- [Writing Picat correctly](#writing-picat-correctly)
- [Common issues](#common-issues)
- Further reading: [SKILL.md](../SKILL.md#further-reading)
- Runnable examples: `../assets/picat/`, one folder per pattern, including `../assets/picat/read-json-instance/` for reading JSON

## Install

```bash
curl -LO https://picat-lang.org/download/picat39_12_linux64.tar.gz
echo "f053b11cccabfb69a3ccd779f2dc1c24cdf889805799bc8c779e6c56da703e4a  picat39_12_linux64.tar.gz" | sha256sum -c
tar -xzf picat39_12_linux64.tar.gz
export PATH="$PWD/Picat:$PATH"
picat --version        # Picat version 3.9#12
```

The archive unpacks to `Picat/`, which holds the `picat` executable and the library modules `cp`, `sat`, `util`, `ordset`, `math` and others. Archives for other platforms are on the [download page](https://picat-lang.org/download.html). Details: [Picat download](https://picat-lang.org/download.html), [Picat guide, install chapter](https://picat-lang.org/download/picat_guide_html/picat_guide.html).

If Picat was unpacked somewhere not on `PATH` (a container image, say), a bare `picat` fails with `picat: not found` (exit 127): call the executable by its full path, or add its directory to `PATH`.

## Quick start

```picat
import cp.

main =>
    X :: 1..10,
    Y :: 1..10,
    X + Y #= 12,
    X #< Y,
    if solve([X, Y]) then
        println([X, Y])
    else
        println(unsat)
    end.
```

Run with `picat quickstart.pi`. It prints `[2,10]`. Every program needs a `main/0` or `main/1`; `picat file.pi` calls it. With `main(Args)`, `picat file.pi instance.json` passes the arguments as a list of strings, so `Args[1]` is the file name as a list of characters.

## Solving

Official: [solving options](https://picat-lang.org/download/picat_guide_html/picat_guide.html) (common options, `cp` options, `sat` options).

| Call | Meaning |
|---|---|
| `solve(Vars)` | first solution, labelling `Vars` |
| `solve(Options, Vars)` | the same with options; **Options come first** |
| `solve([$min(Obj)], Vars)` | optimise; the solution returned is optimal |
| `solve([$max(Obj)], Vars)` | optimise, maximising |
| `solve_all(Vars)` / `findall(Vars, solve(Vars))` | every solution, see [All solutions](#all-solutions) |

**Where errors appear.** Syntax errors go to stderr as `*** SYNTAX ERROR *** (line-range) message` with exit code 1. Runtime errors go to stderr as `*** error(...)`. Undefined predicates go to stderr as `*** Undefined procedure`. `println` writes to stdout.

## All solutions

`findall(Vars, solve(Vars))` returns every solution of `Vars`. `solve_all(Vars)` is the same. Enumerate only the decision variables. Details: [guide, findall and solve](https://picat-lang.org/download/picat_guide_html/picat_guide.html). For all optimal solutions see [SKILL.md](../SKILL.md#all-solutions) and `../assets/picat/all-optimal-vertex-covers/`.

## Writing Picat correctly

These rules are where most failed attempts went wrong. Each one fails silently or with a message that does not point at the cause.

**Clause kinds.** `Head => Body` matches its head: an argument in the head must match the call, it does not unify. So `sk(Cs, Cs) => true.` called as `sk([1], Y)` fails, because `Y` is not matched against `[1]`. Output arguments must be bound in the body (`Out = ...`), and a predicate with output arguments is written with `:-`, which unifies its head. Use `=>` for functions and for predicates whose arguments are all inputs; use `:-` for everything that builds an output (a parser, a predicate that returns a list).

```picat
% wrong: pair(1, Y) fails, because the head [X,X] is matched against the unbound Y
pair(X, [X, X]) => true.

% right: the output is bound in the body
pair(X, Out) => Out = [X, X].

% also right: with :- the head unifies, so the output can be in the head
pair(X, [X, X]) :- true.
```

**Operators.** `**` is power, `^` is XOR. `10**2` is `100`, `10^2` is `8`. `**` also works inside a `cp` constraint (`Z #= 2 ** X` with `X :: 0..3`). `^` inside a constraint raises `invalid_constraint_expression`, so use `**`, or compute the value outside the constraint first.

**Indexing.** `L[I]` and `G[R,C]` index lists and arrays, and `G[R,C]` works for a list of lists as well as for `new_array`. Chained `L[1][2]` is a syntax error (`wrong expression`): bind the row first (`Row = L[1], Row[2]`) or use `L[1,2]`.

**Index as a condition.** `if IsLast[T] then` and `if not IsLast[T] then` raise `invalid_subgoal:index_operator`. An index is a value, not a goal. Compare it (`if IsLast[T] == 1 then`) and store flags as 0/1 integers.

**Booleans from comprehensions.** A relational operator outside a constraint or an `if` condition stays an unevaluated term. `[K == N : K in 1..2]` gives `[1 == 4, 2 == 4]`, not booleans, and `if X[T] == true` misbehaves. Compute a flag in an `if` inside a `foreach` or a helper predicate, or make it a 0/1 decision variable with `#<=>`.

**Characters.** A letter is a character literal: `$a` is `a`, and `[$a, $b]` prints `ab`. Quoted digits and punctuation do not compare as characters: `C >= '0'` and `$'5' >= $'0'` fail with `Wrong function in expression`, and a bare `$0` is the integer 0. Compare codes with `ord/1` instead: `ord(C) >= 48, ord(C) =< 57` for digits, `ord(C) == 123` for `{`.

**Reading files and JSON.** Picat 3.9 has no JSON library: `json_decode` and `parse_json` are undefined (`Undefined procedure`). Read the text with `read_file_chars(Path)` and parse it in Picat. `../assets/picat/read-json-instance/model.pi` is a working reader for objects, arrays, integers and strings, with a `main(Args)` that reads the file given on the command line; copy it into a model.

## Common issues

| Symptom | Likely cause | Fix |
|---|---|---|
| `instantiation_error` on an output value, a list element or a global constraint argument such as `[X + 5, Y]` | arithmetic outside a constraint is computed at once while `X` is still unbound | name the value first: `S #= X + Y`, then use `S` |
| `instantiation_error` on `L = [W[I]*X[I] : I in 1..N]` | list comprehension outside a constraint | keep it inside `sum(...) #= S` or `$max(...)`, or build the list with `foreach` and `#=` |
| `type_error(integer, ...)` on `L[I]` | indexing by a decision variable | `element/3`, `element0/3`, `matrix_element/4` |
| Model fails silently, optimum is not optimal | `solve` arguments swapped: `solve([X], [$max(X)])` labels only the options list | `solve([$max(X)], [X])` |
| `X = X + 1` fails | variables are single-assignment | accumulate with `:=` in a loop, or use `sum/1` |
| `dvar_expected` or `free_var_not_allowed` | a variable (often an output) has no domain | give it a domain with `::` and a constraint |
| `invalid_constraint_exp` | a global constraint inside `#\/`, `#=>`, `#<=>` | state the condition with arithmetic |
| Whole program stops with `error(failed, main/0)` | a constraint posting failed (infeasible), outside an `if` | wrap the posting in `if (...) then ... else ... end` |
| `wrong list format` syntax error | a missing `]` or `,` | check the line range printed with the error |
| `Undefined procedure` / `existence_error` | misnamed predicate or missing `import` | check the name and the module that defines it |
| `Undefined procedure` for `json_decode` or `parse_json` | Picat 3.9 has no JSON library | read with `read_file_chars` and parse; see `assets/picat/read-json-instance/` |
| `picat: not found`, exit 127 | the `picat` executable is not on `PATH` | call it by its full path, or add its directory to `PATH` (see [Install](#install)) |
| `Undefined procedure: char/1` | Picat has no `char/1` | `chr/1` turns a code into a character (`chr(48)` is `0`); `ord/1` turns a character into its code |
| `predicate_used_as_function` | a predicate written where a value is expected, such as `X = jr(...)` | call it as a goal, `jr(Out)`, and read `Out`; or define it with `=` if it returns a value |
| Program prints nothing for a parsed value, or the call fails | `=>` head with an output argument, matched not unified | bind outputs in the body or use `:-`; see [Writing Picat correctly](#writing-picat-correctly) |
| `10^2` gives `8`, or `^` inside a constraint raises `invalid_constraint_expression` | `^` is XOR, not power | write `**` for power |
| `wrong expression` on `L[1][2]` | chained indexing | `L[1,2]`, or bind `Row = L[1]` first |
| `invalid_subgoal:index_operator` on `if IsLast[T]` | an index used as a goal | compare it: `if IsLast[T] == 1` |
| A comprehension of comparisons prints `1 == 4` terms, and an `if` on it takes the wrong branch | relational operators stay terms outside constraints and `if` conditions | build the flag in an `if` inside a `foreach`, or use a 0/1 variable with `#<=>` |
| `Wrong function in expression: '0'` on `C >= '0'` | a quoted digit is not a character literal | compare `ord(C)` with numbers; `$a` is a letter |

Deeper notes on the traps above: [guide, constraints and solving](https://picat-lang.org/download/picat_guide_html/picat_guide.html).
