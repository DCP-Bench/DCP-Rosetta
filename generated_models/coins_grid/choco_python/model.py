# coins_grid: a Choco-solver (Python) model from DCP Rosetta.
# Download the `coins_grid.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/coins_grid.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python coins_grid.py coins_grid.json

from pychoco.model import Model


def create_model(instance):
    """Place coins on an n by n grid, at most one per cell and exactly c in every row
    and every column, so that the sum of the squared horizontal distances of the coins
    from the main diagonal is as small as possible."""
    n = instance["n"]  # the grid has n rows and n columns
    c = instance["c"]  # the number of coins in each row and in each column

    model = Model()

    # x[i][j] is 1 when there is a coin in cell (i, j) and 0 when the cell is empty
    x = [[model.intvar(0, 1, name=f"x_{i}_{j}") for j in range(n)] for i in range(n)]
    # z is the total squared distance of the coins from the main diagonal; each of the
    # at most n * n coins contributes at most (n - 1) ** 2
    z = model.intvar(0, n * n * (n - 1) ** 2, name="z")

    # Each row holds exactly c coins.
    for i in range(n):
        model.sum(x[i], "=", c).post()
    # Each column holds exactly c coins.
    for j in range(n):
        model.sum([x[i][j] for i in range(n)], "=", c).post()

    # Every cell with its cost: a coin in cell (i, j) is |i - j| cells from the diagonal,
    # so it costs (i - j) ** 2.
    cells = [x[i][j] for i in range(n) for j in range(n)]
    costs = [(i - j) ** 2 for i in range(n) for j in range(n)]
    # The costs of the coins add up to z.
    model.scalar(cells, costs, "=", z).post()

    # Minimise the squared distance of the coins from the diagonal.
    return model, {"x": x, "z": z}, {"objective": z, "maximize": False}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
