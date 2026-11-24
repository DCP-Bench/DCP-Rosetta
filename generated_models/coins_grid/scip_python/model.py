# coins_grid: a SCIP (Python) model from DCP Rosetta.
# Download the `coins_grid.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/coins_grid.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python coins_grid.py coins_grid.json

from pyscipopt import Model
import numpy as np


def create_model(instance):
    """Place coins on an n by n grid so that every row and every column holds
    exactly c coins and no cell holds more than one coin, while the sum of the
    squared horizontal distances of the coins from the main diagonal is as
    small as possible."""
    n = instance["n"]  # the grid is n by n: rows and columns 0 to n - 1
    c = instance["c"]  # the number of coins every row and every column must hold

    model = Model("coins_grid")

    # x[i, j] is 1 when cell (i, j) holds a coin, and 0 when it is empty.
    # A binary is enough for "at most one coin per cell".
    x = model.addMatrixVar((n, n), vtype="B", name="x")

    # Each row holds exactly c coins.
    model.addMatrixCons(x.sum(axis=1) == c)
    # Each column holds exactly c coins.
    model.addMatrixCons(x.sum(axis=0) == c)

    # Cell (i, j) lies j - i columns from the main diagonal of its row: to the right
    # when j - i is positive, to the left when negative. A coin there contributes
    # (j - i) ** 2, and dist[i, j] holds that value.
    idx = np.arange(n)
    dist = (idx[None, :] - idx[:, None]) ** 2

    # z is the total squared distance of all coins from the main diagonal: the objective.
    z = (x * dist).sum()
    model.setObjective(z, "minimize")

    return model, {"x": x, "z": z}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
