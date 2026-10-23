# idp_z3: how this integration realises the submission contract

Read [the submission contract](../CONTRACT.md) first; this file only says how FO(.) on
IDP-Z3 expresses it. Runner: [run.py](run.py), self-contained (it does not use
`runner/runtime.py`, although the image carries a copy): it parses the model exactly as
written, binds the instance into a generated structure, and drives z3 itself.
[metadata.yaml](metadata.yaml) declares `instance_binding: reshaped`: the runner's own
`refusal()` decides which instance fields no model can bind (see [Instance](#instance)).

## Submission file

One FO(.) knowledge base, `model.idp`: exactly one `vocabulary`, a `theory`, and
optionally a `structure` of your own. It is not a program: the runner
never calls a `procedure` or `main` block, and no other file of yours is staged.

## Entrypoint

There is no function. The runner parses the file with `IDP.from_str` and reads:

- the single vocabulary (more than one is an error: "A submission must declare exactly
  one vocabulary");
- the symbols named like the declared outputs (see [Outputs](#outputs));
- the symbols named like instance fields, which it interprets (see [Instance](#instance));
- an optional nullary `minimize: () -> Int` or `maximize: () -> Int` (see [Objective](#objective)).

Every theory and every structure in the file, plus the generated one, is combined into
one `Theory`.

## Instance

All instance data arrives in a generated `structure _dcp_instance:<vocabulary>`, the way
FO(.) hands data to a knowledge base; the instance JSON never appears in the model. FO(.)
type ranges must be integer literals (`type Row := {1..n()}` is a parse error), so that
structure also interprets the types the data sizes. Nothing is substituted into the model
text: a leftover `${n}` is an ordinary FO(.) parse error ("Expected IDPFLOAT or INT").

**1. Symbols named like a field.** Every instance field (or reshaped piece, below) whose
name is a symbol (function or predicate) declared in the vocabulary, and which no
`structure` of your own interprets, is interpreted in the generated structure. Indices
are **0-based**, like the JSON:

| Instance field | Declare | Runner writes |
| --- | --- | --- |
| `n: 5` | `n: () -> Int` | `n := 5.` |
| `p: true` | `p: () -> Bool` | `p := true.` |
| `w: [7, 8]` | `type I <: Int`, `w: I -> Int` | `w := {0->7, 1->8}.`, `I := {0..1}.` |
| `cost: [[..],[..]]` (2x3) | `cost: Task * Person -> Int` | `cost := {(0,0)->.., ...}.`, `Task := {0..1}.`, `Person := {0..2}.` |
| `flag: [true, false]` | `flag: I -> Bool` | `flag := {0}.` (the set of true indices) |

- **Index types are sized from the data** only when declared `type T <: Int` with no
  range and interpreted nowhere else: axis K of the field gives `T := {0..len-1}` (`{}`
  for length 0). Two fields that would size one type differently are an error ("type T
  would be sized both 3 and 4").
- The number of argument types must equal the field's number of dimensions, else an
  error ("x is declared with 2 arguments but the instance field has 1 dimensions").
- A `-> Bool` symbol is interpreted as the set of indices whose value is JSON `true`;
  anything else in it (an integer `1`) counts as false. Bind a 0/1 integer field as
  `-> Int` and compare with `= 1`.
- A field the model does not declare is ignored, whatever its type. A symbol interpreted
  in your own `structure` is **not** bound: the instance value is ignored.

**2. `type Range_f <: Int` is `{1..f}`** for an integer scalar field `f`, when the type
is interpreted nowhere else: `type Range_n <: Int` with `n: 8` gives `Range_n := {1..8}.`
(`{}` when `f < 1`). A `Range_` type naming a field that is not an integer scalar is an
error ("type Range_m is {1..m}, but m is not an integer scalar field of the instance"),
and a `Range_` type cannot index an instance array, whose indices start at 0 ("type
Range_n is {1..n}, so it cannot index the instance array w ..."); declare a separate
`type I <: Int` for that.

**3. `type T <: Int` with `T_size: () -> Int` is `{1..v}`**, where `v` is the value the
theory gives `T_size` from the instance data alone (`sized()` in run.py). The runner
interprets `T` provisionally as `{}`, lets IDP-Z3 simplify the theory, and reads the
integer it folded `T_size() = <expression>.` to:

```
type Pos <: Int
Pos_size: () -> Int
...
Pos_size() = sum{{ demand(i) | i in Car }}.    // in the theory
```

Use it for a length that is no single field: `n() + 2`, `2 * k()`, a total over an array.
`sum{{ }}`, `#{ }` and `+ - * /` over data fold; `max{ }`, `min{ }` and `^` do not
(`base() ^ n()` is a type error in IDP-Z3 0.12.1). A `T_size` that does not fold to an
integer is an error ("type Pos is sized by Pos_size, which the theory must define from
instance data alone, as `Pos_size() = <expression>.`"). For a length set by the largest
value, size the type by a sum that bounds it and make the output partial (see
[Outputs](#outputs)).

Values derived from the data belong in the theory, written with the data constants
(`n() * (n() * n() + 1) / 2`); IDP-Z3 folds them before solving.

```
vocabulary {
    type I <: Int                  // sized from npv's length
    budget: () -> Int
    npv: I -> Int
    cash_flow: I -> Int
    x: I -> Bool                   // declared output
    z: () -> Int                   // declared output
    maximize: () -> Int
}
theory {
    sum{{ cash_flow(i) | i in I: x(i) }} =< budget().
    z() = sum{{ npv(i) | i in I: x(i) }}.
    maximize() = z().
}
```

**Reshaping.** Fields FO(.) cannot interpret as they are are reshaped first (`pieces()`
in run.py):

1. A scalar, or a rectangular list of one scalar type, binds unchanged; a nonempty list
   of rows also gives `<field>_len` (each row's length).
2. A ragged list of rows whose items share one shape and one scalar type binds as
   `<field>` padded to the longest row with `0` (`false` for Booleans; rows of arrays gain
   a dimension, padded with zero blocks), plus `<field>_len`. Read `F(i, j)` only for `j`
   below `F_len(i)`: padding can equal a real value.
3. Rows of one length whose columns differ in type bind one piece per column, `<field>_1`,
   `<field>_2`, ... (numbered from 1), each by rules 1 and 2 without splitting again;
   `<field>` itself is not bound.
4. Otherwise, rows (all nonempty) whose first items are scalars of one type bind as
   `<field>_1` (the first items) and `<field>_2` (the rest of each row, by rule 1 or 2).
   `R: [[7, [1, 1], [1, 2]], [9, [2, 2]]]` gives `R_1 := {0->7, 1->9}` and `R_2` (the
   padded cells, `I * J * K -> Int`) with `R_2_len`.
5. Anything else raises `` Instance field `F` is ragged or mixes types in a way this
   integration cannot bind: only the shapes in the rules of pieces() are reshaped ``.

Each piece and each `_len` is bound only if the model declares a symbol of that name.

**Refusals.** A refusal of the data is status `unsupported` (evaluator reason
`unsupported_capability`), and happens only for a declared name:

- a declared field of rule-5 shape;
- a declared string or float value: "instance values of type str cannot be bound into
  FO(.)" (an undeclared string field or column is ignored: bind only the integer columns
  of a mixed row, such as `movies_2`, `movies_3`);
- two instance fields that bind under one declared name (`` instance fields `F` and `G`
  both bind as `F_len` ``).

**Which problems are withheld.** `generation.next_work` withholds a problem for this
integration only when run.py's `refusal(name, value)` rejects a field (other than `name`
and `note`) in some instance, i.e. a rule-5 shape no model could bind. Strings and floats
are not a shape problem and withhold nothing.

## Outputs

Each declared output is a symbol with exactly the output's name. After solving, the runner
collects the ground atoms of that symbol, evaluates each in the z3 model (with model
completion), and nests them by argument value in ascending order, first argument
outermost:

- `z: () -> Int` or `p: () -> Bool` is a scalar;
- `queens: Range_n -> Range_n` is a list ordered by `Range_n` ascending, whatever the
  range starts at (`Range_n` gives n entries);
- `grid: R * C -> Int` is a list of lists.

`-> Bool` reads back as JSON `true`/`false`, an integer codomain as an integer; any other
value is an error ("Declared outputs must be integer or Boolean"). A total output must
cover its argument types ("A declared output must be total over its argument types"); a
name with no ground atoms is "Declared output huey is not a symbol of the vocabulary".

**Partial outputs.** An output shorter than its argument type is declared as a partial
function with a domain predicate defined from the data, and is read (and blocked during
enumeration) only on the tuples where the predicate holds in the model:

```
gap: Range_n -> Bool
diffs: Range_n -> Int (domain: gap)               // n-1 entries
...
{ ! i in Range_n: gap(i) <- i < n(). }            // in the theory
! i in Range_n: gap(i) & i < n() => diffs(i) = abs(x(i + 1) - x(i)).
```

IDP-Z3 does not use the definition when checking well-definedness: every sentence that
applies `diffs` needs `gap(...)` in its guard, and `x(i + 1)` needs a guard keeping
`i + 1` inside the type, else it stops with "Domain error: ... is not a tautology".
Other symbols are auxiliary and never reported.

## Objective

Declare a nullary integer `minimize: () -> Int` **or** `maximize: () -> Int` (a codomain
that is `Int` or a type `<: Int`) and define it in the theory
(`minimize() = sum{{ cost(t, p) | t in Task, p in Person: x(t, p) }}.`). Both, or one
with arguments or a non-integer codomain, is an error. No such symbol means a
satisfaction problem.

## Solving

The runner does not call `Theory.expand` or `Theory.optimize` (`expand` blocks on every
unknown atom, so auxiliary symbols would multiply the models, and treats z3 `unknown` as
`unsat`; `optimize` raises the same error for an unsatisfiable theory and a timeout). It
asserts the theory's assignments into `theory.solver` (a `z3.Solver`) and, for an
optimisation, `theory.optimize_solver` (a `z3.Optimize`), with z3 defaults otherwise.

- **Optimisation**: one `Optimize.check()` on the objective term. `unsat` is `unsat`; any
  other non-`sat` answer is `timeout` ("Candidate optimum was not proven"). The optimum is
  proven only when the objective's lower and upper bounds are equal finite integers;
  unequal bounds are `timeout`, and non-integer (infinite) bounds are `error` ("The
  objective is unbounded: between L and H"). The optimum is then pinned on the solver
  (`objective == best`) for enumeration.
- **Enumeration** (satisfaction, or pinned at the optimum): `check()`; on `sat`, emit the
  declared outputs and add `Or(term != value)` over every ground term of every declared
  output, so only declared outputs are blocked and auxiliary symbols never produce
  repeats. It stops at `solution_limit` (`limit`); `unsat` is exhaustion (`complete`, or
  `unsat` with nothing reported); z3 `unknown` is always `timeout`, never exhaustion.
- **Time**: the deadline is `execution_timeout` from the start of solving (after the
  request is read). Each z3 `check` gets the milliseconds left as z3's `timeout`; none
  left is `timeout`. Parsing and grounding are not under z3's limit: a `SIGALRM` at
  `execution_timeout + 5` s turns into `timeout`, and the evaluator kills the container
  at `execution_timeout + 10` s (`execution_timeout`).
- **Errors**: any other exception (a parse or type error naming line and column, a
  `Range_` or `T_size` type that cannot be sized, a binding error above) is `error`, with the last line of its message as
  detail (`execution_error`); the traceback goes to stderr. A legacy request is
  `unsupported` ("Legacy submissions are not supported by idp_z3").
- The engine's diagnostics go to stderr; only the protocol records go to stdout.

## Compilation

None: parsing, grounding and solving all happen inside the execution budget.
`compilation_timeout` does not apply.

## Environment

Image `dcp-eval/idp_z3:v1` (`python:3.12.11-slim-bookworm`): Python 3.12.11 at
`/usr/local/bin/python`, idp-engine 0.12.1 with the z3-solver 4.11.2.0 it pins, sli-lib
0.4.6, textX 2.3.0, Arpeggio 2.0.3, RestrictedPython 8.5, python-dateutil, six (verified
with `pip list` in the image). The model is FO(.) only and imports nothing; the runner
uses the standard `json`. No edition or size limits, no environment variables set for the
solver.

The evaluator runs the container with no network, a read-only root file system, user
65534, `HOME=/tmp`, the working directory `/tmp` (a 512 MiB tmpfs), `/input` read-only
holding only `model.idp` and `request.json`, 1 CPU and 2048 MiB (verified with the
evaluator's flags: `uid=65534(nobody)`, `/` read-only, `/tmp` 512M tmpfs). The image's
entrypoint is the runner (`python /opt/runner/run.py`); for an ad hoc run override it:
`docker run --rm --network none --entrypoint sh dcp-eval/idp_z3:v1 -c 'python -c "..."'`.

## Traps

- **Two reasons for "refused" data.** Rule-5 shapes, declared strings and floats, and
  name clashes are `unsupported_capability`, not `execution_error`; type sizing conflicts,
  arity mismatches and unsizable `Range_`/`T_size` types are `execution_error`.
- **Your own `structure` interpreting a data symbol** stops the runner from binding it:
  the instance value is silently ignored, which is hardcoding the evaluator rejects on the
  next instance.
- **A declared data symbol that no instance field or piece provides** (a misspelled
  field, or `F_1` of a field whose shape is refused) is not an error: it is simply left
  uninterpreted, a free unknown z3 may choose. Name data symbols exactly as the brief
  lists the fields.
- **`type T` without `<: Int`** is never sized from data and is not numeric.
- **Take every quantity from the instance.** A model that hardcodes the numbers of the
  example passes that instance and is rejected on the next one checked.
- **A 0/1 integer field declared `-> Bool`** binds as all false (only JSON `true` counts),
  without an error naming the field; the evaluator then reports a wrong solution, or
  "Declared outputs cannot extend to a reference solution".
- **Arrays bind 0-based**: an instance holding 1-based coordinates or ids must be shifted
  in the constraint (`r + 1 = lt(k, 0)`), and ragged padding is 0, so compare 1-based ids
  or guard with `F_len`.
- **An unbounded `-> Int` output** is read back as whatever integer z3 picks (the runner
  applies no range), so it can take values the description rules out (negative, above n)
  and the evaluator rejects them with "Declared outputs cannot extend to a reference
  solution". Give every integer output a small range type or explicit bounds in the
  theory (the skill's performance notes say when a range type is too large).
- **An output the brief shows as `int` declared `-> Bool`** comes back as JSON
  `true`/`false` and fails with "Expected integer at x[0][0]"; declare it over
  `type Bit := {0..1}`.
- **`Range_f` counts from 1, instance arrays from 0**: a `Range_` type cannot index an
  instance array (an error, not a silent shift); a list that follows an array goes over
  the array's own index type.
- **The structure name `_dcp_instance`** is the runner's; do not declare it.

- `execution_error` covers everything this runner rejects before solving: a parse or type
  error naming line and column, a declared output that is not a symbol, a `Range_` type
  with no matching field, or data that does not fit its declaration. `execution_timeout` usually means nonlinear
  arithmetic or a type left far larger than the problem needs.

## Example

The pilot fixture [tests/fixtures/model_idp.idp](../../tests/fixtures/model_idp.idp)
(instance fields `n`, `optimize`; outputs `x`, `y`):

```
vocabulary {
    n: () -> Int
    optimize: () -> Bool
    x: () -> Int
    y: () -> Int
    minimize: () -> Int
}
theory {
    0 =< x() & x() =< n().
    0 =< y() & y() =< n().
    optimize() => x() + y() >= n().
    ~optimize() => x() + y() = n().
    minimize() = x() + y().
}
```
