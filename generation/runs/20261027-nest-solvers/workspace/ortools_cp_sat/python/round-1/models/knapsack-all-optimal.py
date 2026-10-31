import json
import sys

from ortools.sat.python import cp_model

with open(sys.argv[1]) as f:
    data = json.load(f)

weights = data["weights"]
values = data["values"]
capacity = data["capacity"]


class Collect(cp_model.CpSolverSolutionCallback):
    def __init__(self, variables):
        super().__init__()
        self.variables = variables
        self.solutions = []

    def on_solution_callback(self):
        self.solutions.append(tuple(self.value(v) for v in self.variables))


def build():
    model = cp_model.CpModel()
    take = [model.new_bool_var(f"take_{i}") for i in range(len(weights))]
    model.add(cp_model.LinearExpr.weighted_sum(take, weights) <= capacity)
    return model, take


# Pass 1: the optimum.
model, take = build()
total = cp_model.LinearExpr.weighted_sum(take, values)
model.maximize(total)
solver = cp_model.CpSolver()
status = solver.solve(model)
if status != cp_model.OPTIMAL:
    raise SystemExit(solver.status_name(status))
best = int(solver.objective_value)

# Pass 2: every selection reaching the optimum, one worker.
model, take = build()
model.add(cp_model.LinearExpr.weighted_sum(take, values) == best)
enumerator = cp_model.CpSolver()
enumerator.parameters.enumerate_all_solutions = True
enumerator.parameters.num_workers = 1
collector = Collect(take)
status = enumerator.solve(model, collector)
if status != cp_model.OPTIMAL:
    raise SystemExit(enumerator.status_name(status))

for sol in sorted(set(collector.solutions)):
    print(json.dumps({"take": list(sol)}))
