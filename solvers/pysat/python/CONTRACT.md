# pysat: how this integration realises the submission contract

Read [the submission contract](../../CONTRACT.md) first; this file only says how PySAT
(Python, SAT and MaxSAT) expresses it. Runner: [run.py](run.py), which takes only `emit`
and `finish` from [runner/runtime.py](../../../runner/runtime.py) and does its own solving.

## Submission file

One Python file, `model.py`. It may import `pysat` (python-sat, with pblib for `PBEnc`)
and the standard library; nothing else is installed, and no other file of yours is staged.
The standalone run block imports `numpy`, which is fine: the runner never executes it.

## Entrypoint

```python
def create_model(instance) -> tuple[pysat.formula.CNF | pysat.formula.WCNF, dict]:
```

The runner imports the file as module `candidate` and calls `create_model(instance)` once.
It must return a 2-tuple `(formula, outputs)`; a third value (an objective) is refused with
an error. Anything the module prints goes to stderr. Models retained before 2026-11-02 name
it `build(instance)`, which the runner still accepts; write `create_model`.

## Instance

`instance` is the JSON object as a plain Python `dict`: integers, Booleans, strings, and
nested `list`s, 0-based.

## Outputs

`outputs` is a non-empty `dict` mapping each declared output name to a leaf or a nested
`list`/`tuple` of leaves. A leaf is one of:

- a Python `int`: a **literal**, reported as `true`/`false` by whether that variable is
  true in the model;
- a Python `bool`: a constant, reported as is;
- a `pysat.integer.Integer`: reported as `decode(model)`;
- a `pysat.integer.LinearExpr` whose terms are all `Integer`s and whose coefficients
  are integers: reported as its value. This is how an output too wide for one `Integer`
  is declared, e.g. `sum(2**k * bit[k])` over 0..1 Integers.

Anything else is an `execution_error`.

## Objective

The **soft clauses of a `WCNF`**: `formula.append(clause, weight=w)`. The runner hands a
`WCNF` with soft clauses to stratified RC2 (`RC2Stratified`), which minimises the total
weight of the soft clauses an assignment **falsifies**; maximising pays the shortfall.
Hard clauses are the constraints. A `CNF`, or a `WCNF` without soft clauses (only its
hard clauses are kept), is a satisfaction problem solved with Glucose 4.2.

## Solving

- Fixed by the runner: Glucose 4.2 (`glucose42`) for satisfaction, `RC2Stratified` over
  the same Glucose for a `WCNF` with soft clauses. No other setting is forced.
- Status: Glucose `True` is an answer, `False` is `unsat` (`complete` once something was
  emitted), `None` (interrupted) is `timeout`. RC2 returns a model only once it has proved
  the optimum; no model is `timeout` if RC2 was interrupted, else `unsat`/`complete`.
- Enumeration adds one blocking clause per answer over the declared outputs: a literal
  flipped, `-x.equals(v)` per `Integer`, the same for each `Integer` a `LinearExpr` sums;
  `bool` leaves are skipped. A repeated output value is re-solved, not emitted. It stops
  with `complete` on unsat, on an empty blocking clause, or, for an optimisation, at the
  first answer whose cost exceeds the first one.
- Time: the budget runs from before `create_model`, so building the formula spends it.
  Each search is stopped by PySAT's interrupt from a timer thread, 0.5 s before the budget
  for Glucose and 2.0 s before it for RC2. A SIGALRM armed for the whole budget can only fire in
  Python code (`create_model`, or between searches); it too is reported as `timeout`.

## Compilation

None.

## Environment

Image `dcp-eval/pysat:v1`: Python 3.12.11 (`/usr/local/bin/python`), python-sat 1.9.dev15
with `pypblib` (compiled at build time, for `PBEnc`) and `six`; the standard library
(`json` included) and nothing else. No licence, no environment variables of note, no
network in the container. For an ad hoc run, `--entrypoint sh` bypasses
`/opt/runner/run.py`.

## Traps

- Every `int` in `outputs` is read as a literal, never as a number: a constant `3` is
  reported as "variable 3 is true". A negative literal `-v` is always reported `false`;
  declare the positive pool id.
- A literal is reported as a Boolean. For an output the brief declares as a 0/1 integer,
  use `Integer(name, 0, 1, vpool=pool)`.
- `cnf.weighted()` turns every clause into a weight-1 soft clause, which the runner then
  reads as objective, not constraint. Add hard clauses with `formula.extend(cnf.clauses)`.
- Because enumeration blocks the combination of Integers a `LinearExpr` output sums,
  every other combination with the same total costs a re-solve.
- `IntegerEngine.add_linear(..., reified=True)` returns `None` when the constraint is a
  bound on one `Integer` already entailed by its domain (`x <= 10` over 0..3). Putting
  that `None` in a clause raises `TypeError` while building (`execution_error`); treat it
  as "always holds" (a clause containing it is already satisfied).

## Example

A complete submission, with the standalone run below:

```python
# knapsack: a PySAT (Python) model from DCP Rosetta.
# Download the `knapsack.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/knapsack.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python knapsack.py knapsack.json

from pysat.formula import IDPool, WCNF
from pysat.pb import PBEnc


def create_model(instance):
    """A hiker chooses which items to pack: as much total value as possible,
    without the items weighing more than the backpack can carry."""
    values = instance["values"]      # values[i]: the value of item i
    weights = instance["weights"]    # weights[i]: the weight of item i
    capacity = instance["capacity"]  # the most weight the backpack can carry

    pool = IDPool()

    # x[i] is true when the hiker packs item i
    x = [pool.id(("x", i)) for i in range(len(values))]

    formula = WCNF()

    # The packed items weigh no more than the backpack can carry.
    formula.extend(PBEnc.leq(lits=x, weights=weights, bound=capacity, vpool=pool).clauses)

    # Pack the most valuable selection. RC2 minimises the weight of the soft clauses it
    # falsifies, so leaving item i behind costs its value.
    for xi, v in zip(x, values):
        if v > 0:
            formula.append([xi], weight=v)

    return formula, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.examples.rc2 import RC2Stratified

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    # falsify as little soft-clause weight as possible
    model = RC2Stratified(formula).compute()

    if model:
        # a literal is true when it is in the model
        value = np.vectorize(lambda lit: lit in model)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
```

## Standalone run

Every model carries a header and a run block like the example's, with `knapsack` replaced
by the problem id, so a reader can copy it from the catalogue and run it with PySAT and
numpy. Nothing else goes in either: the header is the first lines of the file, the run block
the last, and the model sits between them. The runner loads the file as module `candidate`,
so the block never runs during evaluation.

The run block fits the model, so it imports only what that model needs:

- Solving: a model that returns a `WCNF` with soft clauses calls `RC2Stratified`, as in the
  example (plain `RC2` took minutes on some models the stratified form solves in seconds).
  A model that returns a `CNF` solves it once with `Solver`:

  ```python
      from pysat.solvers import Solver
      ...
      solver = Solver(bootstrap_with=formula)
      solver.solve()
      model = solver.get_model()  # None when there is no solution
  ```

- Reading the outputs, by the kind of leaf they hold:
  - `Integer`s: `value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables`;
  - literals: `value = np.vectorize(lambda lit: lit in model)`, under the comment
    `# a literal is true when it is in the model`;
  - both: `value = np.vectorize(lambda v: v.decode(model) if isinstance(v, Integer) else v in model)`,
    using the `Integer` the model imports at the top.

  A `LinearExpr` output has no single decode: the run block adds up its terms,
  `res.const + sum(c * var.decode(model) for var, c in res.terms.items())`.
  `Integer.decode` reads the model by variable number, which works when every output
  appears in the formula; an `Integer` whose clauses were never added is read past the end
  of the model.

A problem whose instance file is empty (`bench/dataset/<problem>/<problem>.json` is `[]`)
has all its data fixed by the statement. Its header and run block are:

```python
# abbots_puzzle: a PySAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/abbots_puzzle.html
# Run it (after `pip install "python-sat[pblib]" numpy`) with:
#   python abbots_puzzle.py
```

```python
if __name__ == "__main__":
    import numpy as np
    from pysat.solvers import Solver

    formula, outputs = create_model({})

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
```
