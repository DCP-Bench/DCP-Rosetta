# heterosquare: a Choco-solver (Python) model from DCP Rosetta.
# Download the `heterosquare.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/heterosquare.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python heterosquare.py heterosquare.json

from pychoco.model import Model


def create_model(instance):
    """A heterosquare of order n is an n by n square of distinct integers from 1 to n^2
    whose row, column and diagonal sums are all different."""
    n = instance["n"]  # the order of the square

    model = Model()

    # x[i][j] is the number in row i, column j.
    x = [[model.intvar(1, n * n, name=f"x_{i}_{j}") for j in range(n)] for i in range(n)]

    # The sums of the rows, the columns and the two diagonals. Each sum adds n
    # numbers of at most n^2, so it is at most n^3.
    row_sums = [model.intvar(1, n ** 3, name=f"row_sum_{i}") for i in range(n)]
    col_sums = [model.intvar(1, n ** 3, name=f"col_sum_{j}") for j in range(n)]
    # diag_sum runs from top left to bottom right, anti_diag_sum from top right to bottom left.
    diag_sum = model.intvar(1, n ** 3, name="diag_sum")
    anti_diag_sum = model.intvar(1, n ** 3, name="anti_diag_sum")

    # The numbers in the square are distinct.
    model.all_different([cell for row in x for cell in row]).post()

    # Each row and column sum is the total of its cells.
    for i in range(n):
        model.sum(x[i], "=", row_sums[i]).post()
        model.sum([x[k][i] for k in range(n)], "=", col_sums[i]).post()

    # Each diagonal sum is the total of its cells.
    model.sum([x[i][i] for i in range(n)], "=", diag_sum).post()
    model.sum([x[i][n - 1 - i] for i in range(n)], "=", anti_diag_sum).post()

    # No two of the row, column and diagonal sums are equal.
    model.all_different(row_sums + col_sums + [diag_sum, anti_diag_sum]).post()

    return model, {"x": x}, None


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
