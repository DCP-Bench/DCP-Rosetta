# coins_grid: a CPMpy model from DCP Rosetta.
# Download the `coins_grid.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/coins_grid.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python coins_grid.py coins_grid.json

import cpmpy as cp
import numpy as np


def create_model(instance):
    """Place coins on an n by n grid, at most one per cell and exactly c in every row
    and every column, so that the sum of the squared horizontal distances of the coins
    from the main diagonal is as small as possible."""
    n = instance["n"]  # the grid has n rows and n columns
    c = instance["c"]  # the number of coins in each row and in each column

    # x[i, j] is 1 when there is a coin in cell (i, j); the domain 0..1 gives at most one coin per cell
    x = cp.intvar(0, 1, shape=(n, n), name="x")
    # z is the sum of the squared horizontal distances of all coins from the main diagonal;
    # each coin adds at most (n - 1) ** 2 and there are at most n * n coins
    z = cp.intvar(0, n * n * (n - 1) ** 2, name="z")

    # A coin in cell (i, j) is |i - j| cells from the diagonal, so it costs (i - j) ** 2
    squared_distance = (np.arange(n).reshape(n, 1) - np.arange(n).reshape(1, n)) ** 2

    model = cp.Model()
    # Each row holds exactly c coins.
    model.add(x.sum(axis=1) == c)
    # Each column holds exactly c coins.
    model.add(x.sum(axis=0) == c)
    # z adds up the squared distances of the cells that hold a coin.
    model.add(z == cp.sum(x * squared_distance))
    # Keep the coins as close to the main diagonal as possible.
    model.minimize(z)

    return model, {"x": x, "z": z}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
