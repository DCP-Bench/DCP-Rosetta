# coins_grid: a hermax (Python) model from DCP Rosetta.
# Download the `coins_grid.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/coins_grid.html
# Then run it on the first instance (after `pip install hermax`):
#   python coins_grid.py coins_grid.json

from hermax.model import Model


def create_model(instance):
    """Place coins on an n-by-n grid so that every row and every column holds exactly c
    coins and each cell holds at most one, while the total of the squared horizontal
    distance from the main diagonal over all coins, (i - j)^2 for a coin in row i and
    column j, is as small as possible."""
    n = instance["n"]  # the grid has n rows and n columns
    c = instance["c"]  # the number of coins every row and every column must hold

    m = Model()

    # x[i][j] is 1 when a coin sits in row i, column j, and 0 otherwise.
    # The output is declared as integers, so the cells are 0..1 integers.
    # the 0..1 domain is condition 4: at most one coin per cell
    x = m.int_matrix("x", n, n, 0, 1)

    # Each row holds exactly c coins.
    for i in range(n):
        m &= (sum(x.row(i)) == c)

    # Each column holds exactly c coins.
    for j in range(n):
        m &= (sum(x.col(j)) == c)

    # z is the total squared horizontal distance from the main diagonal over all coins.
    z = sum((i - j) ** 2 * x[i][j] for i in range(n) for j in range(n))

    # Minimise the total squared distance of the coins from the main diagonal.
    m.obj += z

    return m, {"x": x, "z": z}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
