import json
import sys

from ortools.sat.python import cp_model

with open(sys.argv[1]) as f:
    data = json.load(f)

n = data["n_nodes"]
edges = data["edges"]

model = cp_model.CpModel()
colour = [model.new_int_var(0, n - 1, f"c_{i}") for i in range(n)]
for u, v in edges:
    model.add(colour[u] != colour[v])

# The number of distinct colours equals the largest index plus one at an optimum.
largest = model.new_int_var(0, n - 1, "largest")
model.add_max_equality(largest, colour)
model.minimize(largest)

solver = cp_model.CpSolver()
status = solver.solve(model)
if status != cp_model.OPTIMAL:
    raise SystemExit(solver.status_name(status))

print(json.dumps({"colour": [solver.value(c) for c in colour]}))
