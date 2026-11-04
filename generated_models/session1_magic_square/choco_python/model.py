# session1_magic_square: a Choco-solver (Python) model from DCP Rosetta.
# Download the `session1_magic_square.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_magic_square.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python session1_magic_square.py session1_magic_square.json

from pychoco.model import Model


def create_model(instance):
    """Fill an n x n grid with the different integers 1 to n^2 so that every row,
    column and both diagonals add up to the same sum."""
    n = instance["n"]  # the number of rows and columns of the square

    # The numbers 1 to n^2 add up to n^2 (n^2 + 1) / 2, so each of the n rows
    # must add up to n (n^2 + 1) / 2.
    magic_sum = n * (n * n + 1) // 2

    model = Model()

    # square[i][j] is the number in row i, column j
    square = [[model.intvar(1, n * n, name=f"square_{i}_{j}") for j in range(n)] for i in range(n)]

    # All numbers in the square are different.
    model.all_different([square[i][j] for i in range(n) for j in range(n)]).post()

    # Every row adds up to the magic sum.
    for i in range(n):
        model.sum(square[i], "=", magic_sum).post()

    # Every column adds up to the magic sum.
    for j in range(n):
        model.sum([square[i][j] for i in range(n)], "=", magic_sum).post()

    # The main diagonal adds up to the magic sum.
    model.sum([square[i][i] for i in range(n)], "=", magic_sum).post()

    # The other diagonal adds up to the magic sum.
    model.sum([square[i][n - 1 - i] for i in range(n)], "=", magic_sum).post()

    return model, {"square": square}, None


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
