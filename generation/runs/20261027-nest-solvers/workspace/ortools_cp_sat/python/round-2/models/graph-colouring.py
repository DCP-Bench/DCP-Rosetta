import json
import sys

from ortools.sat.python import cp_model


def main():
    with open(sys.argv[1]) as f:
        data = json.load(f)
    n = data["n_nodes"]
    edges = data["edges"]

    model = cp_model.CpModel()
    colour = [model.new_int_var(0, max(n - 1, 0), f"colour_{i}") for i in range(n)]
    for u, v in edges:
        model.add(colour[u] != colour[v])

    # Minimise the largest colour index; at an optimum the colours are 0..k-1,
    # so this equals the number of distinct colours minus one.
    largest = model.new_int_var(0, max(n - 1, 0), "largest")
    model.add_max_equality(largest, colour)
    model.minimize(largest)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 60
    status = solver.solve(model)
    if status != cp_model.OPTIMAL:
        print(solver.status_name(status), file=sys.stderr)
        sys.exit(1)
    print(json.dumps({"colour": [solver.value(c) for c in colour]}))


if __name__ == "__main__":
    main()
