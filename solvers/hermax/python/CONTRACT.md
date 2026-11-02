# hermax: how this integration realises the submission contract

Read [the submission contract](../../CONTRACT.md) first; this file only says how hermax
(Python, MaxSAT) expresses it. Runner: [run.py](run.py), which takes `emit`, `finish` and
`mapped` from [runner/runtime.py](../../../runner/runtime.py) and does its own solving.

## Submission file

One Python file, `model.py`. It may import `hermax` (which brings `pysat`) and the
standard library; nothing else is installed, and no other file of yours is staged.

## Entrypoint

```python
def create_model(instance) -> tuple[hermax.model.Model, dict]:
```

The runner imports the file as module `candidate` and calls `create_model(instance)` once.
It must return a 2-tuple `(model, outputs)` with `model` a `hermax.model.Model`; the
objective is never returned. Anything the module prints goes to stderr.

Models retained before the rename name it `build(instance)`, with the same return value;
the runner still accepts that name. Write `create_model`.

## Instance

`instance` is the JSON object as a plain Python `dict`: integers, Booleans, strings, and
nested `list`s, 0-based.

## Outputs

`outputs` is a non-empty `dict` mapping each declared output name to variables of the
model, or nested `list`s/`tuple`s of them:

- a `Literal` (from `m.bool`) is reported as `true`/`false`, an `IntVar` as an `int`;
- a vector or matrix (`m.bool_vector`, `m.int_matrix`, ...) may be given whole and is
  decoded by hermax into nested lists;
- a linear expression (`PBExpr`, or a single weighted literal `Term`) with integer
  coefficients is decoded by hermax (`result[expr]`, since 1.2.9). This is how an output too wide for one `IntVar`
  is declared, e.g. `sum(10**(9-i) * digit[i])` over 0..9 IntVars.

Plain Python values (`int`, `bool`) are not accepted (`execution_error`).

## Objective

Minimise a cost with `m.obj += expr` (or `m.obj.add(expr, weight=w)`), where `expr` is a
literal, an `IntVar`, a linear expression, or a sum of these: hermax turns it into weighted
soft clauses. `m.obj += w * lit` pays `w` when `lit` is true, so paying when a literal is
false is `m.obj += w * ~lit`, and maximising a quantity is minimising its complement. The
cost includes the expression's constant and lower bounds (`m.obj += x` with `x` in 3..7
costs 3 at best). The `m.obj[w] += lit` form of hermax 1.2 raises `TypeError` since 1.3.0.
The runner always minimises that cost and reads only whether one exists: `result.cost` is
None when there are no soft clauses, which makes the model a satisfaction problem.

## Solving

- The runner calls `model.solve(time_limit=left)` with hermax's defaults and forces no
  other setting: a model with soft clauses goes to hermax's CoreTrail (the default since 1.3.0), a hard-only model to
  PySAT's Glucose 4 (`g4`).
- Status: `optimum`, or `sat` without soft clauses, is an answer; `unsat` is `unsat`
  (`complete` once something was emitted); `interrupted`, `interrupted_sat` and `unknown`
  are `timeout` (an unproven incumbent is never reported); `error` and any other status
  are `error`.
- Enumeration adds one blocking clause per answer over every `Literal` and `IntVar` under
  the declared outputs, including those a `PBExpr`/`Term` output sums (`x != v` per
  `IntVar`, the flipped literal per `Literal`), and re-solves. A repeated output value is
  re-solved, not emitted. It stops with `complete` on `unsat`, when nothing is left to
  block, or, for an optimisation, at the first answer whose cost exceeds the first one.
- Time: one deadline from the runner's start; each solve gets the time left, and an
  expired deadline before a solve is `timeout`. There is no SIGALRM, so `create_model` itself is
  unbounded until the evaluator stops the container.

## Compilation

None.

## Environment

Image `dcp-eval/hermax:v1`: Python 3.12.11 (`/usr/local/bin/python`), hermax 1.3.0 with
python-sat 1.9.dev17 (and `six`); the standard library (`json` included) and nothing else.
`Model.solve` defaults to CoreTrail (since 1.3.0) for soft clauses and Glucose 4.1 otherwise, which is what
`metadata.json` names. No licence, no environment variables of note, no
network in the container. For an ad hoc run, `--entrypoint sh` bypasses
`/opt/runner/run.py`.

## Traps

- `create_model` has no time limit of its own (see Solving): a slow one ends as
  `execution_timeout`. Give the objective to `m.obj` directly: an auxiliary `IntVar`
  tied to it (`total == sum(...)`, then `m.obj += total`) works since 1.3.0, but its
  encoding still costs time (1.8 s against 0.01 s on a 12-by-12 assignment).
- With `solution_limit > 1`, an output expression must sum only literals and `IntVar`s:
  a derived integer such as `x // 3` inside it cannot be blocked (`execution_error`).
  Tie it to an `IntVar` first.
- Because enumeration blocks the literals and variables an expression output sums, every
  other combination with the same total costs a re-solve.
- A `Literal` output is reported as a Boolean. For an output the brief declares as a
  0/1 integer, use `m.int(name, 0, 1)`.

## Example

A complete submission, with the standalone run below:

```python
# aircraft_landing: a hermax (Python) model from DCP Rosetta.
# Download the `aircraft_landing.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/aircraft_landing.html
# Then run it on the first instance (after `pip install hermax`):
#   python aircraft_landing.py aircraft_landing.json

from hermax.model import Model, sum_expr


def create_model(instance):
    """Land each aircraft inside its time window, keeping the required separation after
    every earlier aircraft, so that the total penalty for landing before or after each
    aircraft's target time is as small as possible."""
    earliest = instance["earliest_landing"]      # earliest[i]: first time aircraft i may land
    latest = instance["latest_landing"]          # latest[i]: last time aircraft i may land
    target = instance["target_landing"]          # target[i]: preferred landing time of aircraft i
    penalty_before = instance["penalty_before"]  # penalty_before[i]: cost per time unit early
    penalty_after = instance["penalty_after"]    # penalty_after[i]: cost per time unit late
    separation = instance["separation_time"]     # separation[i][j]: gap needed when i lands before j
    n = len(earliest)

    m = Model()

    # landing_times[i] is when aircraft i lands, inside its own time window
    landing_times = [m.int(f"landing_time_{i}", earliest[i], latest[i]) for i in range(n)]

    # Aircraft land in the given order, each at least the separation time after every earlier one.
    for i in range(n):
        for j in range(i + 1, n):
            m &= (landing_times[i] + separation[i][j] <= landing_times[j])

    # The penalty of landing aircraft i at time t: per time unit early, or per time unit late.
    def penalty(i, t):
        return penalty_before[i] * max(0, target[i] - t) + penalty_after[i] * max(0, t - target[i])

    # The total penalty sums, per aircraft, its penalty as a step function over its time window.
    total_penalty = sum_expr(
        time.piecewise(base_value=penalty(i, time.lb),
                       steps={t: penalty(i, t) for t in range(time.lb + 1, time.ub + 1)})
        for i, time in enumerate(landing_times))

    # Minimise the total penalty.
    m.obj += total_penalty

    return m, {"landing_times": landing_times, "total_penalty": total_penalty}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
```

## Standalone run

Every model carries the header and the run block of the example, with `aircraft_landing`
replaced by the problem id, so a reader can copy it from the catalogue and run it with
nothing but `pip install hermax`. Nothing else goes in either: the header is the first
lines of the file, the run block the last, and the model sits between them. The runner
loads the file as module `candidate`, so the block never runs during evaluation.

A problem whose instance file is empty (`bench/dataset/<problem>/<problem>.json` is `[]`)
has all its data fixed by the statement. Its header and run block are:

```python
# abbots_puzzle: a hermax (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/abbots_puzzle.html
# Run it (after `pip install hermax`) with:
#   python abbots_puzzle.py
```

```python
if __name__ == "__main__":
    model, outputs = create_model({})
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
```

The pilot fixture [tests/fixtures/model_hermax.py](../../../tests/fixtures/model_hermax.py)
(instance fields `n`, `optimize`; outputs `x`, `y`) is in the same form.
