"""All optimal 0/1 knapsack selections with Yices.

First the optimal value is found by tightening the value bound. Then a fresh
context asserts the capacity and value == optimum, and every selection is
enumerated with a no-good over the item variables.
"""
import json
import sys
from pathlib import Path

from yices import Context, Model, Status, Terms, Types

inst = json.loads(Path(sys.argv[1]).read_text())
weights = inst["weights"]
values = inst["values"]
capacity = inst["capacity"]
n = len(weights)

if n == 0:
    print(json.dumps({"take": []}))
    sys.exit(0)

BOOL = Types.bool_type()
zero = Terms.integer(0)
take = [Terms.new_uninterpreted_term(BOOL, f"take_{i}") for i in range(n)]
total_weight = Terms.sum([Terms.ite(take[i], Terms.integer(weights[i]), zero) for i in range(n)])
total_value = Terms.sum([Terms.ite(take[i], Terms.integer(values[i]), zero) for i in range(n)])


def fits(ctx):
    """Assert that the chosen items fit in the knapsack."""
    ctx.assert_formula(Terms.arith_leq_atom(total_weight, Terms.integer(capacity)))


# Pass 1: the optimal value.
ctx = Context()
fits(ctx)
best = None
while ctx.check_context() == Status.SAT:
    model = Model.from_context(ctx, 1)
    best = sum(v for v, t in zip(values, [1 if model.get_value(x) else 0 for x in take]) if t)
    model.dispose()
    ctx.assert_formula(Terms.arith_gt_atom(total_value, Terms.integer(best)))
ctx.dispose()

if best is None:
    print(json.dumps({"status": "unsatisfiable"}))
    sys.exit(0)

# Pass 2: every selection of the optimal value, each printed once.
ctx = Context()
fits(ctx)
ctx.assert_formula(Terms.arith_eq_atom(total_value, Terms.integer(best)))
while ctx.check_context() == Status.SAT:
    model = Model.from_context(ctx, 1)
    chosen = [1 if model.get_value(t) else 0 for t in take]
    model.dispose()
    print(json.dumps({"take": chosen}))
    # No-good: at least one item differs from this selection.
    differs = [Terms.ynot(t) if c else t for t, c in zip(take, chosen)]
    ctx.assert_formula(Terms.yor(differs))
ctx.dispose()
