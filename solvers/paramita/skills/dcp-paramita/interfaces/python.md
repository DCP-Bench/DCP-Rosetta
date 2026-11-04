# Paramita in Python

What holds in every interface (concepts, statuses, enumeration strategy, solver-level pitfalls) is in
[SKILL.md](../SKILL.md). Call signatures: [references/python/api.md](../references/python/api.md).
Encodings and modelling advice: [references/python/modelling.md](../references/python/modelling.md).

## Install

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install paramita
paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
```

The solver plugins are not in the wheel. Each `paramita plugins build` fetches
[paramita-plugins](https://codeberg.org/paramita/paramita-plugins), builds one plugin and
installs it where paramita looks by default (`~/.local/share/paramita/plugins`). It needs
Linux, git, cmake and a C++ compiler; EvalMaxSAT also needs zlib. Satisfaction needs only
CaDiCaL, optimisation only EvalMaxSAT. The pblib encoders
(`'#pb-to-cnf-encoders/pblib'`) are optional: paramita encodes pseudo-Boolean constraints
without them.

To build the exact versions tested here, check out commit
`a9c15a0bbaca86e89eaa1cff5d4d62a4218596cb` of paramita-plugins and build from it:

```bash
git clone https://codeberg.org/paramita/paramita-plugins && git -C paramita-plugins checkout a9c15a0bbaca86e89eaa1cff5d4d62a4218596cb
P="$PWD/paramita-plugins"
paramita plugins build cmake -j 4 "file://$P#sat-solvers/cadical-3.0.0"
paramita plugins build cmake -j 4 "file://$P#maxsat-solvers/mse22-EvalMaxSAT2022"
```

If the EvalMaxSAT build fails while configuring, its `FindZLIB.cmake` is downloading zlib
from zlib.net; use a system zlib or the zlib 1.3.2 GitHub release (SHA-256
`bb329a0a2cd0274d05519d61c667c062e06990d72e125ee2dfa8de64f0119d16`).

Verify: `SatSolver.from_name("Cadical300")` and `MaxSatSolver.from_name("EvalMaxSAT2022")`
must both construct without an error.

## Quick start

```python
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf
from paramita.solvers import SatSolver

a, b, c = Bool("a"), Bool("b"), Bool("c")
constraints = [a | b, ~a | ~c, sum([a, b, c]) == 2]

pool = DimacsVariablePool()
solver = SatSolver.from_name("Cadical300")
for e in constraints:
    add_to_container(e, to_cnf, solver, pool)

if solver.solve():
    true = {abs(lit) for lit in solver.model() if lit > 0}
    print({name: pool.get_variable(v) in true for name, v in [("a", a), ("b", b), ("c", c)]})
else:
    print("unsatisfiable")
```

Prints `{'a': False, 'b': True, 'c': True}`. Every model is a standalone program: it builds, solves
and prints. Worked examples, each with a README (problem, what it shows, run, expected output):

| Pattern | Example |
|---|---|
| satisfy: one solution, one-hot cells | [queens-one](../assets/python/queens-one/README.md) |
| all solutions, blocking clauses over the answer Booleans | [queens-all](../assets/python/queens-all/README.md) |
| maximise (MaxSAT) | [knapsack-max](../assets/python/knapsack-max/README.md) |
| all optimal solutions | [all-optimal](../assets/python/all-optimal/README.md) |
| minimise, instance read from a JSON file | [colouring-json](../assets/python/colouring-json/README.md) |
| infeasible, read from the status | [infeasible](../assets/python/infeasible/README.md) |
| scheduling with deadlines, reading start times | [scheduling](../assets/python/scheduling/README.md) |

## Modelling

Full reference: [Python API](https://ulog.udl.cat/static/doc/paramita/). Calls are in [references/api.md](../references/python/api.md).

| The description says | Expression |
|---|---|
| a and b / a or b / not a | `a & b`, `a \| b`, `~a`; `And`/`Or` take two operands or one list: `Or([a, b, c])` (`Or(a, b, c)` and `Or(a)` raise TypeError) |
| if a then b | `If(a, b)` |
| a exactly when b | `Iff(a, b)` |
| exactly / at least / at most k of these | `sum(bs) == k`, `sum(bs) >= k`, `sum(bs) <= k` |
| weighted capacity, budget | `sum(w * b for w, b in zip(ws, bs)) <= cap` |
| a condition holds when r is chosen (reified) | `If(r, sum(bs) >= 2)`; both ways: `Iff(r, 2*a + b <= 2)` |
| x differs from y (as Bools) | `Iff(a, ~b)`; exactly one of two: `a + b == 1` |

- PB comparisons take negative coefficients and sums on both sides
  (`a + b <= c + r`). Weights are integers.
- `Xor` and `^` build an expression but `to_cnf` rejects it ("Invalid operation when
  converting to NNF+"): write `(a & ~b) | (~a & b)` or `a + b == 1`.
- `Bool("x")` is identified by its name: the same name is the same variable.
  Build names from indices (`Bool(f"x_{i}_{v}")`) and keep them unique per meaning.
- `==` on Bools builds an expression, never a Python bool: do not put Bools in
  sets, dict keys or `if` tests. The converse: `sum([])` is the int 0, so
  `sum([]) == k` and `sum([]) >= k` are Python bools, not expressions. Skip the
  constraint when the list is empty (check `len(bs)` first); never pass such a bool
  into `If` or `~`, because `If(a, False)` silently forces `a` false.
- Integers are 32-bit inside Paramita: a coefficient beyond ±2^31 is a TypeError, and a
  sum whose value leaves that range wraps silently. Scale large data down or split the
  sum.
- `Bool | (PB comparison)`, `If(PB, Bool)` and `If(Bool, PB)` are all accepted by `to_cnf`
  (checked on small cases against brute force). A PB comparison that is a constant in
  Python is not an expression: see Common issues.
- Integers as Booleans (one-hot, unary, binary), global-style constraints as PB
  constraints (all different, element, table, no-overlap, product), symmetry, wide
  ranges and weight shrinking: [references/modelling.md](../references/python/modelling.md).

## Solving

**Satisfaction.** Add every expression with `add_to_container(expr, to_cnf, solver, pool)`,
then `solver.solve()`:

| Result | Meaning |
|---|---|
| `True` | a model; read it with `solver.model()` (one signed literal per variable) |
| `False` | proven unsatisfiable |
| `None` | the conflict budget ran out before an answer (only with a budget, see below) |

```python
true = {abs(lit) for lit in solver.model() if lit > 0}
value = pool.get_variable(a) in true          # abs(lit) ignores the sign; read the list
```

**All solutions.** After each model, add a clause that differs from it in at least one
answer Boolean, and solve again; `False` means the list is complete. Block only the
answer variables: auxiliary variables make duplicates of the same answer.
See [queens-all](../assets/python/queens-all/README.md).

**Optimisation (MaxSAT).** `add_to_weighted_container(objective, subject_to, to_cnf, ms, pool)`
with `ms = MaxSatSolver.from_name("EvalMaxSAT2022")` **maximises** the linear objective and
returns the objective's constant part; the optimum is `constant + ms.benefit()`. To
minimise, pass the negated objective and negate the result. `subject_to` must be one
expression: wrap a list with `And(list)`. `ms.solve()` returns `MAXSAT_ANSWER.OPTIMAL`,
`SATISFIABLE`, `UNSATISFIABLE` or `UNKNOWN`; only `OPTIMAL` is a proven result.
See [knapsack-max](../assets/python/knapsack-max/README.md) and
[colouring-json](../assets/python/colouring-json/README.md).

**All optimal solutions.** Solve for the optimum, then add `objective == optimum` as a
hard constraint to a **fresh** solver and enumerate the answer Booleans as above. See
[all-optimal](../assets/python/all-optimal/README.md).

**Time limits.** CaDiCaL takes only `SolvingBudget(num_conflicts=N)`: call `solve` in
rounds of N conflicts and check the clock between them. EvalMaxSAT takes no budget at all:
run it in a child process and kill that process at the deadline; a child that has not
finished is a timeout, not a result.

**Recursion.** The default PB encoder recurses once per term. A single sum of about 5000
Bools segfaults on the default 8 MB stack (2000 was fine). Run under `ulimit -s unlimited`
(or a larger stack), or split the sum into smaller ones.

## Readable models

Write for a student reading the model for the first time, in the words of the problem
statement, not of the API:

- a docstring that states the problem in a sentence or two;
- a comment on each input field, saying what it holds (`weights[i]: the weight of item i`);
- a comment on each decision variable, saying what it means (`x[i] is true when item i is packed`);
- a comment on each group of constraints and on the objective;
- the plainest expression that says it (`sum(w * xi for w, xi in zip(weights, x)) <= capacity`),
  and variables kept as lists or nested lists so they print as a whole.

Build the model in one function that encodes it into a formula, as a CNF or WCNF file
holds a problem: a `CnfFormula` for a satisfaction problem, or a `WcnfFormula` whose hard
clauses are the constraints and whose soft clauses are the objective (maximised; negate
an objective to minimise it). Return the formula with the pool that numbered its Bools,
and the variables to print. For example:

```python
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
```

A satisfaction model adds its constraints one by one with
`add_to_container(constraint, to_cnf, formula, pool)`. Every Bool that is printed must
appear in some constraint, or the solver's model has no value for it.

To solve, copy the formula into a solver; paramita has no call that loads a formula
object into one. For a `CnfFormula`, `solver.add_clauses(formula.clauses())` on a
`SatSolver`; for a `WcnfFormula`, `add_clauses(formula.hard_clauses())` and then
`add_clause(clause, weight)` for each of `formula.soft_clauses()` on a `MaxSatSolver`.
Read each output with
`evaluate(e, {pool.decode_literal(abs(lit)).name: lit > 0 for lit in solver.model()})`; it
gives a Boolean for a Bool and an integer for a sum, and `numpy.vectorize` applies it to a
nested list in one call.

## Common issues

| Problem | Likely cause | Fix |
|---|---|---|
| `RuntimeError: Invalid operation when converting to NNF+` | `Xor` or `^` in an expression | Expand: `(a & ~b) \| (~a & b)` |
| `TypeError` from `And`/`Or` | three operands, or one bare operand | `Or([a, b, c])`, or nest two-operand calls |
| A Bool in a set, a dict key or an `if` test misbehaves | `==` on Bools builds an expression, and a Bool is not a Python bool | keep Booleans as expressions; map them to ids with `pool.get_variable` |
| `sum([]) == k` gives a Python `bool` | an empty sum is the int 0 | skip empty sums (see Modelling) |
| A constraint silently forces a Bool false, e.g. `If(a, sum([]) >= 1)` makes `a` false | `sum([]) >= 1` is Python `False`, and `If` with a Python bool on one side is not a dropped constraint | build the constraint only when the list is non-empty |
| A unary chain gives too small a value (e.g. a makespan of 0) | an end time that is always at least `t` (end >= t with `t` at most the duration) was left out of the clauses instead of asserted | assert such a fact as a unit clause (`m[t]`, `s[b][t]`), not as an `If` with a constant |
| `SyntaxError` at the top of the file | a comment such as `# ... encoding: ...` in lines 1-2 is a Python coding declaration | move encoding notes below line 2 |
| Optimum or direction looks wrong | objective not negated for a minimise, or the constant part not added | `optimum = constant + ms.benefit()`; negate for minimise |

Solver-level issues are in [SKILL.md](../SKILL.md#common-issues).
