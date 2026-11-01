# calvin_puzzle: a Choco-solver (Python) model from DCP Rosetta.
# Download the `calvin_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/calvin_puzzle.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python calvin_puzzle.py calvin_puzzle.json

from pychoco.model import Model


def create_model(instance):
    """Fill an n by n grid with the numbers 1 to n^2 in sequence. The next number goes either
    exactly three squares away horizontally or vertically, or exactly two squares away
    diagonally from the previous one."""
    n = instance["n"]                 # the grid has n rows and n columns
    n_squares = n * n                 # the number of squares, which is also the largest number

    # The steps from one square to the next, as (row change, column change): three squares
    # along a row or column, or two squares along a diagonal.
    moves = [(3, 0), (-3, 0), (0, 3), (0, -3), (2, 2), (2, -2), (-2, 2), (-2, -2)]

    model = Model()

    # x_flat[c] is the number written in square c, with the squares counted row by row from 1.
    x_flat = [model.intvar(1, n_squares, name=f"x_{c}") for c in range(n_squares)]
    # where[k] is the square that holds the number k + 1.
    where = [model.intvar(1, n_squares, name=f"where_{k}") for k in range(n_squares)]

    # Every number from 1 to n^2 is written in exactly one square, and where gives the same
    # placement from the number's side.
    model.all_different(x_flat).post()
    model.inverse_channeling(x_flat, where, 1, 1).post()

    # The pairs of squares one allowed step apart, staying on the grid.
    one_step_apart = []
    for i in range(n):
        for j in range(n):
            for di, dj in moves:
                if 0 <= i + di < n and 0 <= j + dj < n:
                    one_step_apart.append([i * n + j + 1, (i + di) * n + (j + dj) + 1])

    # Each number is placed one allowed step from the number before it.
    for k in range(n_squares - 1):
        model.table([where[k], where[k + 1]], one_step_apart).post()

    # The grid: x[i][j] is the number in row i, column j.
    x = [[x_flat[i * n + j] for j in range(n)] for i in range(n)]

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
