# coins_grid: a PyCSP3 model from DCP Rosetta.
# Download the `coins_grid.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/coins_grid.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python coins_grid.py coins_grid.json

from pycsp3 import *


def create_model(instance):
    """Place coins on an n by n grid so that every row and every column holds
    exactly c coins, and at most one coin sits in each cell. The sum of the
    quadratic horizontal distances (i - j)^2 from the main diagonal of the cells
    holding a coin must be as small as possible."""
    n = instance["n"]  # the grid is n by n
    c = instance["c"]  # the number of coins in each row and in each column

    # x[i][j] = 1 when a coin is placed in row i, column j; 0 otherwise.
    # The 0/1 domain gives at most one coin per cell.
    x = VarArray(size=[n, n], dom={0, 1})

    # z = the sum of the squared distances (i - j)^2 of all cells holding a coin.
    # The largest possible value: c coins in each of the n rows, each at most (n - 1)^2 from the diagonal.
    max_distance = (n - 1) ** 2
    z = Var(dom=range(n * c * max_distance + 1))

    satisfy(
        # In each row exactly c coins are placed.
        [Sum(x[i]) == c for i in range(n)],
        # In each column exactly c coins are placed.
        [Sum(x[:, j]) == c for j in range(n)],
        # z is the sum of (i - j)^2 over the cells that hold a coin.
        z == Sum(x[i][j] * (i - j) ** 2 for i in range(n) for j in range(n)),
    )

    # Minimise the sum of the quadratic horizontal distances from the main diagonal.
    minimize(z)

    return {"x": x, "z": z}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is OPTIMUM:
        print("x", "=")
        for row in outputs["x"]:
            print(values(row))
    else:
        print("No solution:", status())
