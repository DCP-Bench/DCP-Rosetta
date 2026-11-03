# candies: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `candies.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/candies.html
# Then run it on the first instance (after `pip install ortools`):
#   python candies.py candies.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Children stand in a line, each with a rating. Every child gets at least one candy, and
    a child with a higher rating than a neighbour gets more candies than that neighbour."""
    ratings = instance["ratings"]  # ratings[i]: the rating of the child at position i
    n = len(ratings)               # the number of children

    model = cp_model.CpModel()

    # x[i] is the number of candies the child at position i gets. No child needs more than n.
    x = [model.new_int_var(1, n, f"x_{i}") for i in range(n)]
    # z is the total number of candies
    z = model.new_int_var(1, n * n, "z")

    # The total is the sum of the candies given to the children.
    model.add(z == sum(x))
    # Every child gets at least one candy, so the total is at least n.
    model.add(z >= n)

    # Of two neighbours, the child with the higher rating gets more candies.
    for i in range(1, n):
        if ratings[i - 1] > ratings[i]:
            model.add(x[i - 1] > x[i])
        elif ratings[i - 1] < ratings[i]:
            model.add(x[i - 1] < x[i])

    # Minimize the total number of candies.
    model.minimize(z)

    return model, {"z": z, "x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
