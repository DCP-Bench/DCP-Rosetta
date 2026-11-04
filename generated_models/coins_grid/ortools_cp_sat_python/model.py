# coins_grid: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `coins_grid.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/coins_grid.html
# Then run it on the first instance (after `pip install ortools`):
#   python coins_grid.py coins_grid.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Place coins on an n by n grid, at most one per cell and exactly c in every row
    and every column, so that the sum of the squared horizontal distances of the coins
    from the main diagonal is as small as possible."""
    n = instance["n"]  # the grid has n rows and n columns
    c = instance["c"]  # the number of coins in each row and in each column

    model = cp_model.CpModel()

    # x[i][j] is 1 when a coin is in cell (i, j), and 0 when the cell is empty
    x = [[model.new_int_var(0, 1, f"x_{i}_{j}") for j in range(n)] for i in range(n)]
    # z is the total squared distance of the coins from the main diagonal, at most n * n * (n - 1) ** 2
    z = model.new_int_var(0, n * n * (n - 1) ** 2, "z")

    # Each row holds exactly c coins.
    for i in range(n):
        model.add(sum(x[i]) == c)
    # Each column holds exactly c coins.
    for j in range(n):
        model.add(sum(x[i][j] for i in range(n)) == c)
    # A coin in cell (i, j) is |i - j| cells from the diagonal, so it costs (i - j) ** 2.
    model.add(z == sum(x[i][j] * (i - j) ** 2 for i in range(n) for j in range(n)))

    # Keep the coins as close to the main diagonal as possible.
    model.minimize(z)

    return model, {"x": x, "z": z}


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
