# coins_grid: an Exact (Python) model from DCP Rosetta.
# Download the `coins_grid.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/coins_grid.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python coins_grid.py coins_grid.json

from exact import Exact


def create_model(instance):
    """Place coins on an n by n grid, at most one per cell and exactly c in every row
    and every column, so that the sum of the squared horizontal distances of the coins
    from the main diagonal is as small as possible."""
    n = instance["n"]  # the grid has n rows and n columns
    c = instance["c"]  # the number of coins in each row and in each column

    solver = Exact()

    # Exact identifies its variables by name.
    # x[i][j] is 1 when there is a coin in cell (i, j), and 0 when the cell is empty.
    x = [[f"x_{i}_{j}" for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(n):
            solver.addVariable(x[i][j], 0, 1)

    # Each row holds exactly c coins.
    for i in range(n):
        solver.addConstraint([(1, x[i][j]) for j in range(n)], True, c, True, c)

    # Each column holds exactly c coins.
    for j in range(n):
        solver.addConstraint([(1, x[i][j]) for i in range(n)], True, c, True, c)

    # z is the total squared distance of the coins from the main diagonal. Its upper bound
    # is the largest such total for n * c coins.
    solver.addVariable("z", 0, n * c * (n - 1) ** 2)

    # A coin in cell (i, j) is |i - j| columns from the diagonal, so it costs (i - j) ** 2.
    distance_terms = [((i - j) ** 2, x[i][j]) for i in range(n) for j in range(n) if i != j]
    solver.addConstraint(distance_terms + [(-1, "z")], True, 0, True, 0)

    # Keep the total squared distance from the diagonal as small as possible.
    solver.setObjective(distance_terms, minimize=True)

    return solver, {"x": x, "z": "z"}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
