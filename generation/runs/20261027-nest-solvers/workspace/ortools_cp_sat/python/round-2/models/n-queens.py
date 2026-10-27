import json
import sys

from ortools.sat.python import cp_model


def main():
    with open(sys.argv[1]) as f:
        data = json.load(f)
    n = data["n"]

    model = cp_model.CpModel()
    col = [model.new_int_var(0, n - 1, f"col_{i}") for i in range(n)]
    model.add_all_different(col)
    model.add_all_different([col[i] + i for i in range(n)])
    model.add_all_different([col[i] - i for i in range(n)])

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 60
    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print(json.dumps({"queens": [solver.value(c) for c in col]}))
    elif status == cp_model.INFEASIBLE:
        print(json.dumps({"status": "unsatisfiable"}))
    else:
        print(solver.status_name(status), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
