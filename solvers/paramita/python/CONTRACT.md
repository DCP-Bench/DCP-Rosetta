# paramita_python: how this integration realises the submission contract

Read [the submission contract](../../CONTRACT.md) first; this file only says how Paramita
(Python, SAT and MaxSAT) expresses it. Runner: [run.py](run.py), which takes only `emit`
and `finish` from [runner/runtime.py](../../../runner/runtime.py) and does its own solving.

## Submission file

One Python file, `model.py`, written against `paramita.modelling`, `paramita.containers`
(paramita 1.2.0) and the standard library; no modelling layer of the integration's own is
installed beside paramita, and no other file of yours is staged. The model encodes its own
constraints, so it imports the encoder (`to_cnf`) and the container classes itself. Do not
create or call a solver in `create_model`: the runner solves. The standalone run block
creates its own solver and imports `numpy`, which is fine: the runner never executes it.

## Entrypoint

```python
def create_model(instance) -> tuple[tuple[CnfFormula | WcnfFormula, DimacsVariablePool],
                                    dict]:
```

The runner imports the file as module `candidate` and calls `create_model(instance)` once.
Models retained before 2026-11-02 name it `build(instance)`, which the runner still
accepts by name, but only if it returns the form below; write `create_model`. It must
return exactly `(formula, pool), outputs`:

- `formula` is a `paramita.containers.CnfFormula` for a satisfaction problem, or a
  `WcnfFormula` for an optimisation problem;
- `pool` is the `DimacsVariablePool` the model encoded with; the runner decodes with it;
- `outputs` is described below.

Anything else is refused with `error` (`execution_error`) and a message naming the form:
a list or a 3-tuple (an objective as a third value, `("maximize", expr)`, is refused:
an objective is the soft clauses of a `WcnfFormula`), a formula without its pool, a
formula that is neither class, a pool that is not a `DimacsVariablePool`, or empty
`outputs`. The runner encodes nothing: it copies the clauses into a solver. Anything the
module prints, at import or in `create_model`, goes to stderr.

## Instance

`instance` is the JSON object as a plain Python `dict`: integers, Booleans, strings, and
nested `list`s, 0-based. Every field is there, including ragged or mixed-type ones the
brief lists as unbindable (as parsed JSON) and extra keys (`name`, `note`) to ignore. A
problem without instance fields still receives `instance`.

## Outputs

`outputs` is a non-empty `dict` mapping each declared output name to a leaf or a nested
`list`/`tuple` of leaves. Each is read with `evaluate` over the solver's assignment of
the named Bools, decoded through `pool`. A leaf is one of:

- a `Bool`, or any Boolean expression over Bools (`a & b`, `x + y == n`): reported as a
  JSON Boolean;
- an integer expression over Bools (`sum(w * b) + c`, `1 * b`, `-e`): reported as a JSON
  integer;
- a Python `int` or `bool` constant: reported as is.

Anything else (a string, a float) is an `error` (`execution_error`). An output the
brief declares as an integer must be an integer expression: a cell that is a Bool goes
out as `1 * b`, since a bare Bool is reported as a Boolean.

Integer outputs are computed by the runner in Python integers, not in paramita's 32-bit
`evaluate`: an output beyond 32 bits is exact as long as each coefficient fits in 32 bits
(`sum(10**k * digit_k)` for a ten-digit number is fine). A Bool or Boolean expression
inside such a sum counts as 0 or 1.

## Objective

The soft clauses of a `WcnfFormula`, encoded by
`add_to_weighted_container(objective, subject_to, to_cnf, formula, pool)`: the hard
clauses are the constraints, and the soft clauses are the objective, which is maximised
(EvalMaxSAT maximises the satisfied soft weight). A model that minimises passes the
negated objective. A soft clause with weight 0 still counts as one. A `CnfFormula`, or
a `WcnfFormula` without soft clauses (only its hard clauses are kept), is a satisfaction
problem.

## Solving

- Fixed by the runner: a `CnfFormula` or a `WcnfFormula` without soft clauses is loaded
  into `SatSolver.from_name("Cadical300")` (CaDiCaL 3.0.0) with `add_clauses`; a
  `WcnfFormula` with soft clauses is loaded into `MaxSatSolver.from_name("EvalMaxSAT2022")`:
  the hard clauses, then `add_clause(clause, weight)` per soft clause.
- Satisfaction status: CaDiCaL `True` is an answer; `False` before any answer is
  `unsat`, after one `complete`; still undecided at the deadline is `timeout`. Reaching
  the solution limit is `limit`, which is not a failure.
- Optimisation status: only a proven optimum (`OPTIMAL`) is reported; `UNSATISFIABLE`
  is `unsat`; a search not finished at the deadline is `timeout` (`the optimum was not
  proven`), with nothing reported, which the evaluator records as `execution_timeout`;
  an exception in the MaxSAT process, or its death without an answer, is `error`.
- Enumeration blocks the declared outputs, not the whole assignment: after each answer
  the runner adds one clause over every Bool named in `outputs`, ruling out that
  combination. Two assignments that agree on every output count once: a repeated output
  value is re-solved, not emitted. Unsat after a blocking clause is `complete`, and so is
  an output that names no Bool (nothing to block). A Bool the solver never saw is
  unconstrained and reported `false`.
- Optimisation enumeration: EvalMaxSAT has no budget and ignores interrupts, so it runs
  in a forked child that solves, sends the output Bools of an optimum, adds a hard
  blocking clause over them and solves again, until the answer is no longer optimal or
  its benefit falls below the first optimum's. The parent emits each optimum as it
  arrives, the first at once. A child that crashes or raises, or does not finish by the
  deadline, ends the run as `timeout` (`the optimum was proven, the enumeration was
  not`); the solutions already emitted stand.
- Time: the budget runs from before `create_model`, so building spends it. The forked
  EvalMaxSAT child is waited on until 0.5 s before the runner's deadline (itself 0.5 s
  before the budget) and then killed. CaDiCaL supports only a conflict budget, so it runs
  in calls of 5000 conflicts and the clock is checked between them. A SIGALRM at the
  budget turns a hang in Python (in `create_model`, or while waiting on a solver) into
  `timeout`.
- Stack and recursion: the default PB encoder, which the model calls through `to_cnf`,
  recurses once per term, so a PB constraint over about a thousand Bools overflows the
  default 8 MB stack (signal 11). Before anything else the runner raises its stack soft
  limit to the hard limit and re-executes itself, and sets Python's recursion limit to
  1 000 000, so a flat `sum` over thousands of Bools (a chain of nested additions) does
  not exceed it either.
- A legacy request is `unsupported`.

## Compilation

None.

## Environment

Image `dcp-eval/paramita_python:v1` (`python:3.12.11-slim-bookworm`): Python 3.12.11
(`/usr/local/bin/python`), paramita 1.2.0 from PyPI, and plugins built from
[paramita-plugins](https://codeberg.org/paramita/paramita-plugins) at commit
`a9c15a0bbaca86e89eaa1cff5d4d62a4218596cb`: the SAT solver Cadical300 (CaDiCaL 3.0.0),
the MaxSAT solver EvalMaxSAT2022, and the PB-to-CNF encoders pblib (under
`/usr/local/share/paramita/plugins`) and pysat (under `/usr/share/paramita/plugins`).
Only the plugins' shared objects are copied into the runtime image, so no compiler is
present. The standard library (`json` included) and paramita's own dependencies; no
licence, no size limit, no environment variables of note.

Inside the container: no network, a read-only filesystem except `/tmp` (512 MB tmpfs,
the working directory, and `HOME`), user 65534, the submission and `request.json` under
`/input`, no `/dataset`. The paramita plugins print to file descriptor 1 when they load,
and EvalMaxSAT writes `c ...` lines there; the runner points fd 1 at stderr before any
plugin loads and writes the protocol to a saved copy. The image's entrypoint is the
runner (`python /opt/runner/run.py`); for an ad hoc run override it, e.g. `docker run
--rm --network none --entrypoint sh dcp-eval/paramita_python:v1 -c '...'`.

## Traps

- Every Bool an output uses must appear in the formula. The runner reads a Bool the
  formula never mentions as `false`, and a standalone run cannot read it at all (its
  `truth` has no entry for it). Constrain it, or leave it out of `outputs`.
- A satisfaction problem must not add soft clauses: a `WcnfFormula` with soft clauses
  is an optimisation, and only its optima would be reported.
- A `WcnfFormula` is not a `ClauseContainer` for `add_to_container`. An optimisation
  model passes all its hard constraints through `add_to_weighted_container`'s
  `subject_to`, as `And(constraints)`; `And` of an empty list raises.
- Integers are 32-bit inside paramita. A coefficient outside that range is a `TypeError`
  while building (`execution_error`); a constraint or objective whose value leaves it
  wraps around without an error, and the evaluator then rejects the wrong value. Only
  integer outputs are read exactly beyond 32 bits (see Outputs).
- `Xor` and `^` are not supported by `to_cnf` (`execution_error`): expand into `&`, `|`,
  `~`.
- A bare `Bool` under an integer output is reported as `true`/`false`, not `1`/`0`:
  write `1 * b`.
- Because enumeration blocks the combination of Bools an output is built from, an
  integer output over Bools that several assignments map to one value (a unary sum
  without order constraints, a sum over many Bools) costs a re-solve per assignment with
  the same value.
- A `dict` inside an output is walked as one and comes out as a JSON object
  (`invalid_output`): return lists.

## Example

A complete submission, with the standalone run below:

```python
# knapsack: a Paramita (Python) model from DCP Rosetta.
# Download the `knapsack.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/knapsack.html
# Then install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python knapsack.py knapsack.json

from paramita.containers import WcnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_weighted_container, to_cnf


def create_model(instance):
    """A hiker chooses which items to pack: as much total value as possible,
    without the items weighing more than the backpack can carry."""
    values = instance["values"]      # values[i]: the value of item i
    weights = instance["weights"]    # weights[i]: the weight of item i
    capacity = instance["capacity"]  # the most weight the backpack can carry

    # x[i] is true when the hiker packs item i
    x = [Bool(f"x_{i}") for i in range(len(values))]

    # The packed items weigh no more than the backpack can carry.
    fits = sum(w * xi for w, xi in zip(weights, x)) <= capacity

    # Pack the most valuable selection.
    packed_value = sum(v * xi for v, xi in zip(values, x))

    # Encode into a weighted formula: the constraint as hard clauses, the value to maximise
    # as soft clauses. The pool gives each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(packed_value, fits, to_cnf, formula, pool)

    return (formula, pool), {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import MAXSAT_ANSWER, MaxSatSolver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    (formula, pool), outputs = create_model(instances[index])

    solver = MaxSatSolver.from_name("EvalMaxSAT2022")
    # copy the formula into the solver: the hard clauses, then each soft clause with its weight
    solver.add_clauses(formula.hard_clauses())
    for weight, clause in formula.soft_clauses():
        solver.add_clause(clause, weight)

    if solver.solve() == MAXSAT_ANSWER.OPTIMAL:
        # the value of every variable by name: a literal is true when it is positive
        truth = {pool.decode_literal(abs(lit)).name: lit > 0 for lit in solver.model()}
        value = np.vectorize(lambda e: evaluate(e, truth))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
```

## Standalone run

Every model carries a header and a run block like the example's, with `knapsack` replaced
by the problem id, so a reader can copy it from the catalogue and run it with paramita and
numpy. The header lists the plugin build commands for the one solver the model uses:
EvalMaxSAT for an optimisation model (as in the example), CaDiCaL for a satisfaction model.
Nothing else goes in either: the header is the first lines of the file, the run block the
last, and the model sits between them. The runner loads the file as module `candidate`, so
the block never runs during evaluation.

The run block copies the formula into the solver, because paramita has no call that loads
a formula object into a solver: `add_clauses(formula.hard_clauses())` and
`add_clause(clause, weight)` per soft clause for EvalMaxSAT, as in the example, or
`add_clauses(formula.clauses())` for CaDiCaL. Outputs are read with `evaluate(e, truth)`
over the solver's model by name, where `truth` maps every variable name in the model to its
value (decoded through `pool`); `numpy.vectorize` applies it to nested lists. The header and run block of a satisfaction
model, `bin_packing`:

```python
# bin_packing: a Paramita (Python) model from DCP Rosetta.
# Download the `bin_packing.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bin_packing.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python bin_packing.py bin_packing.json
```

```python
if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import SatSolver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    (formula, pool), outputs = create_model(instances[index])

    solver = SatSolver.from_name("Cadical300")
    # copy the formula into the solver
    solver.add_clauses(formula.clauses())

    if solver.solve():
        # the value of every variable by name: a literal is true when it is positive
        truth = {pool.decode_literal(abs(lit)).name: lit > 0 for lit in solver.model()}
        value = np.vectorize(lambda e: evaluate(e, truth))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
```

A problem whose instance file is empty (`bench/dataset/<problem>/<problem>.json` is `[]`)
has all its data fixed by the statement. Its header and run block are:

```python
# abbots_puzzle: a Paramita (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/abbots_puzzle.html
# Install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python abbots_puzzle.py
```

```python
if __name__ == "__main__":
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import SatSolver

    (formula, pool), outputs = create_model({})

    solver = SatSolver.from_name("Cadical300")
    # copy the formula into the solver
    solver.add_clauses(formula.clauses())

    if solver.solve():
        # the value of every variable by name: a literal is true when it is positive
        truth = {pool.decode_literal(abs(lit)).name: lit > 0 for lit in solver.model()}
        value = np.vectorize(lambda e: evaluate(e, truth))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
```
