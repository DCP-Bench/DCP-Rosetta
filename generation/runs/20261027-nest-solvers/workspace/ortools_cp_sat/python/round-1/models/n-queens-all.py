import json
import sys

from ortools.sat.python import cp_model

with open(sys.argv[1]) as f:
    data = json.load(f)

n = data["n"]


class Collect(cp_model.CpSolverSolutionCallback):
    def __init__(self, variables):
        super().__init__()
        self.variables = variables
        self.solutions = []

    def on_solution_callback(self):
        self.solutions.append(tuple(self.value(v) for v in self.variables))


model = cp_model.CpModel()
col = [model.new_int_var(0, n - 1, f"q_{i}") for i in range(n)]
model.add_all_different(col)
model.add_all_different([col[i] + i for i in range(n)])
model.add_all_different([col[i] - i for i in range(n)])

solver = cp_model.CpSolver()
solver.parameters.enumerate_all_solutions = True
solver.parameters.num_workers = 1
collector = Collect(col)
status = solver.solve(model, collector)
if status != cp_model.OPTIMAL:
    raise SystemExit(solver.status_name(status))

for sol in sorted(set(collector.solutions)):
    print(json.dumps({"queens": list(sol)}))
