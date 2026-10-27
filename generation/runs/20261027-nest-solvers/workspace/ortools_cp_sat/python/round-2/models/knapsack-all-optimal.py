import json
import sys

from ortools.sat.python import cp_model


class Collect(cp_model.CpSolverSolutionCallback):
    def __init__(self, variables):
        super().__init__()
        self.variables = variables
        self.count = 0

    def on_solution_callback(self):
        self.count += 1
        take = [int(self.boolean_value(v)) for v in self.variables]
        print(json.dumps({"take": take}), flush=True)


def main():
    with open(sys.argv[1]) as f:
        data = json.load(f)
    weights = data["weights"]
    values = data["values"]
    capacity = data["capacity"]

    model = cp_model.CpModel()
    take = [model.new_bool_var(f"take_{i}") for i in range(len(weights))]
    model.add(cp_model.LinearExpr.weighted_sum(take, weights) <= capacity)
    total = cp_model.LinearExpr.weighted_sum(take, values)
    model.maximize(total)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 60
    status = solver.solve(model)
    if status != cp_model.OPTIMAL:
        print(solver.status_name(status), file=sys.stderr)
        sys.exit(1)
    best = int(solver.objective_value)

    model.add(total == best)
    model.clear_objective()

    enumerator = cp_model.CpSolver()
    enumerator.parameters.enumerate_all_solutions = True
    enumerator.parameters.num_workers = 1
    enumerator.parameters.max_time_in_seconds = 600
    collector = Collect(take)
    status = enumerator.solve(model, collector)
    if status == cp_model.INFEASIBLE:
        print(json.dumps({"status": "unsatisfiable"}))
    elif status != cp_model.OPTIMAL:
        print(enumerator.status_name(status), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
