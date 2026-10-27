import json
import sys

from pychoco.model import Model

# Usage: python3 model.py instance.json
# Reads the items and the capacity from a JSON file; every size comes from the data.
with open(sys.argv[1]) as f:
    data = json.load(f)
weights, values, capacity = data["weights"], data["values"], data["capacity"]

model = Model()
take = [model.boolvar(name=f"take{i}") for i in range(len(weights))]
model.scalar(take, weights, "<=", capacity).post()
profit = model.intvar(0, sum(values), name="profit")
model.scalar(take, values, "=", profit).post()

solution = model.get_solver().find_optimal_solution(profit, True)
if solution is None:
    print("no solution")
else:
    chosen = [i for i, t in enumerate(take) if solution.get_int_val(t) == 1]
    print("Items:", chosen)
    print("Profit:", solution.get_int_val(profit))
