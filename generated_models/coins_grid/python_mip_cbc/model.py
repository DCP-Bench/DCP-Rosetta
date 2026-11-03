# coins_grid: a Python-MIP (Python) model from DCP Rosetta.
# Download the `coins_grid.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/coins_grid.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python coins_grid.py coins_grid.json

import mip


def create_model(instance):
    """Place coins on an n by n grid, at most one per cell and exactly c in every row
    and every column, so that the sum of the squared horizontal distances of the coins
    from the main diagonal is as small as possible."""
    n = instance["n"]  # the grid has n rows and n columns
    c = instance["c"]  # the number of coins in each row and in each column

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # x[i][j] is 1 when there is a coin in cell (i, j), and 0 when the cell is empty.
    x = [[model.add_var(f"x_{i}_{j}", var_type=mip.BINARY) for j in range(n)] for i in range(n)]
    # z is the total squared distance of the coins from the main diagonal. Each of the n rows
    # holds c coins, each at distance at most n - 1.
    z = model.add_var("z", lb=0, ub=c * n * (n - 1) ** 2, var_type=mip.INTEGER)

    # Each row holds exactly c coins.
    for i in range(n):
        model += mip.xsum(x[i]) == c

    # Each column holds exactly c coins.
    for j in range(n):
        model += mip.xsum(x[i][j] for i in range(n)) == c

    # A coin in cell (i, j) is j - i cells to the right of the diagonal, and z is the sum of
    # the squares of these distances over the coins.
    model += z == mip.xsum((j - i) ** 2 * x[i][j] for i in range(n) for j in range(n))

    # Make z as small as possible.
    model.objective = z

    return model, {"x": x, "z": z}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
