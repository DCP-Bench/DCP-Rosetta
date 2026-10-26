"""0/1 knapsack with Yices, maximising the total value.

Each item is a Boolean term. The value is tightened after each model until
the solver proves the best value optimal.
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

ctx = Context()

# The chosen items fit in the knapsack.
ctx.assert_formula(Terms.arith_leq_atom(total_weight, Terms.integer(capacity)))

best = None
best_take = None
while ctx.check_context() == Status.SAT:
    model = Model.from_context(ctx, 1)
    chosen = [1 if model.get_value(t) else 0 for t in take]
    model.dispose()
    best_take = chosen
    best = sum(v for v, t in zip(values, chosen) if t)
    # Ask for a selection of strictly higher value.
    ctx.assert_formula(Terms.arith_gt_atom(total_value, Terms.integer(best)))
ctx.dispose()

if best_take is None:
    print(json.dumps({"status": "unsatisfiable"}))
else:
    print(json.dumps({"take": best_take}))
