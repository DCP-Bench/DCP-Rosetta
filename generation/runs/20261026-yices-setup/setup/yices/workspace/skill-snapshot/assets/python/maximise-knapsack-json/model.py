# 0/1 knapsack, maximise value. Reads its data from a JSON file (first argument, default data.json).
import json
import sys
from pathlib import Path
from yices import Context, Model, Status, Terms, Types

path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("data.json")
data = json.loads(path.read_text())
items = data["items"]                         # any number of items: sizes come from the data
weights = [it["weight"] for it in items]
values = [it["value"] for it in items]
capacity = data["capacity"]
num = Terms.integer

take = [Terms.new_uninterpreted_term(Types.bool_type(), f"take{i}") for i in range(len(items))]

def total(coefs):                              # sum of coef * (take ? 1 : 0)
    return Terms.sum([Terms.mul(num(c), Terms.ite(t, num(1), num(0))) for c, t in zip(coefs, take)])

ctx = Context()
# the chosen items fit into the knapsack
ctx.assert_formula(Terms.arith_leq_atom(total(weights), num(capacity)))
# ragged list: conflicts[i] holds any number of items that cannot be taken together with item i
for i, row in enumerate(data.get("conflicts", [])):
    for j in row:
        ctx.assert_formula(Terms.ynot(Terms.yand([take[i], take[j]])))
objective = total(values)

# maximise: demand a strictly larger value after every solution; UNSAT proves the last one optimal
best, chosen = None, None
while ctx.check_context() == Status.SAT:
    model = Model.from_context(ctx, 1)
    best = model.get_value(objective)
    chosen = [i for i, t in enumerate(take) if model.get_bool_value(t)]
    model.dispose()
    ctx.assert_formula(Terms.arith_gt_atom(objective, num(best)))
if best is None:
    print("Infeasible")
else:
    print("Objective:", best, "(optimal)")
    print("Items:", chosen)
