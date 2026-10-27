import json
import sys

from ortools.sat.python import cp_model

with open(sys.argv[1]) as f:
    data = json.load(f)

weights = data["weights"]
values = data["values"]
capacity = data["capacity"]

model = cp_model.CpModel()
take = [model.new_bool_var(f"take_{i}") for i in range(len(weights))]
model.add(cp_model.LinearExpr.weighted_sum(take, weights) <= capacity)
model.maximize(cp_model.LinearExpr.weighted_sum(take, values))

solver = cp_model.CpSolver()
status = solver.solve(model)
if status != cp_model.OPTIMAL:
    raise SystemExit(solver.status_name(status))

print(json.dumps({"take": [solver.value(t) for t in take]}))
