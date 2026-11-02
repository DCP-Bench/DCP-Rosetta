# coins_grid: a Z3 (Python) model from DCP Rosetta.
# Download the `coins_grid.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/coins_grid.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python coins_grid.py coins_grid.json

import z3


def create_model(instance):
    """Place coins on an n by n grid, at most one per cell and exactly c in every row
    and every column, so that the sum of the squared horizontal distances of the coins
    from the main diagonal is as small as possible."""
    n = instance["n"]  # the grid has n rows and n columns
    c = instance["c"]  # the number of coins in each row and in each column

    # x[i][j] is 1 when there is a coin in cell (i, j), and 0 when the cell is empty
    x = [[z3.Int(f"x_{i}_{j}") for j in range(n)] for i in range(n)]
    # z is the total squared distance of the coins from the main diagonal
    z = z3.Int("z")

    solver = z3.Optimize()

    # Each cell holds at most one coin.
    solver.add([z3.And(x[i][j] >= 0, x[i][j] <= 1) for i in range(n) for j in range(n)])

    # Each row holds exactly c coins.
    solver.add([z3.Sum(row) == c for row in x])

    # Each column holds exactly c coins.
    solver.add([z3.Sum([x[i][j] for i in range(n)]) == c for j in range(n)])

    # A coin in cell (i, j) is |i - j| cells from the diagonal, so it costs (i - j) ** 2.
    solver.add(z == z3.Sum([x[i][j] * (i - j) ** 2 for i in range(n) for j in range(n)]))

    # Keep the coins as close to the main diagonal as possible.
    solver.minimize(z)

    return solver, {"x": x, "z": z}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
