import json
import sys

from ortools.sat.python import cp_model


def main():
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
    solver.parameters.max_time_in_seconds = 60
    status = solver.solve(model)
    if status != cp_model.OPTIMAL:
        print(solver.status_name(status), file=sys.stderr)
        sys.exit(1)
    print(json.dumps({"take": [int(solver.boolean_value(t)) for t in take]}))


if __name__ == "__main__":
    main()
