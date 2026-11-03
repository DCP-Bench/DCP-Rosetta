# sudoku: a Choco-solver (Python) model from DCP Rosetta.
# Download the `sudoku.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/sudoku.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python sudoku.py sudoku.json

from math import isqrt

from pychoco.model import Model


def create_model(instance):
    """Complete a partly filled Sudoku grid so that each row, column and block holds every
    digit from 1 to n exactly once, keeping the digits already given."""
    given = instance["input_grid"]  # given[r][c]: the digit in row r, column c, or 0 when the cell is empty
    n = len(given)                  # side of the grid
    box = isqrt(n)                  # side of a block

    model = Model()

    # grid[r][c] is the digit in row r, column c
    grid = [[model.intvar(1, n, name=f"grid_{r}_{c}") for c in range(n)] for r in range(n)]

    # The given digits stay where they are.
    for r in range(n):
        for c in range(n):
            if given[r][c] != 0:
                model.arithm(grid[r][c], "=", given[r][c]).post()

    # Every row holds each digit once.
    for r in range(n):
        model.all_different(grid[r]).post()

    # Every column holds each digit once.
    for c in range(n):
        model.all_different([grid[r][c] for r in range(n)]).post()

    # Every block holds each digit once.
    for i in range(0, n, box):
        for j in range(0, n, box):
            model.all_different([grid[r][c] for r in range(i, i + box) for c in range(j, j + box)]).post()

    return model, {"grid": grid}, None


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
