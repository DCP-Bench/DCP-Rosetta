# coins_grid: a PuLP (Python) model from DCP Rosetta.
# Download the `coins_grid.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/coins_grid.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python coins_grid.py coins_grid.json

import pulp


def create_model(instance):
    """Place coins on an n by n grid, at most one per cell and exactly c in every row
    and every column, so that the sum of the squared horizontal distances of the coins
    from the main diagonal is as small as possible."""
    n = instance["n"]  # the grid has n rows and n columns
    c = instance["c"]  # the number of coins in each row and in each column

    problem = pulp.LpProblem("coins_grid", pulp.LpMinimize)

    # x[i][j] is 1 when a coin sits in row i, column j, and 0 when the cell is empty.
    x = [[pulp.LpVariable(f"x_{i}_{j}", cat="Binary") for j in range(n)] for i in range(n)]

    # z is the squared distance of the coins from the main diagonal, summed over the coins.
    # A coin is at most n - 1 cells from the diagonal and there are n * c coins, which
    # bounds z.
    z = pulp.LpVariable("z", 0, n * c * (n - 1) ** 2, cat="Integer")

    # A coin in row i, column j is |i - j| cells from the diagonal, so it costs (i - j) ** 2.
    cost = pulp.lpSum((i - j) ** 2 * x[i][j] for i in range(n) for j in range(n))
    # z is the total cost.
    problem += z == cost

    # Make the total squared distance as small as possible.
    problem += cost

    # Every row holds exactly c coins.
    for i in range(n):
        problem += pulp.lpSum(x[i]) == c

    # Every column holds exactly c coins.
    for j in range(n):
        problem += pulp.lpSum(x[i][j] for i in range(n)) == c

    return problem, {"x": x, "z": z}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
