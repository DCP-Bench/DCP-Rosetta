# sudoku: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `sudoku.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/sudoku.html
# Then run it on the first instance (after `pip install ortools`):
#   python sudoku.py sudoku.json

import math

from ortools.sat.python import cp_model


def create_model(instance):
    """Sudoku: fill a 9 x 9 grid with the digits 1 to 9 so that every row, every
    column and every 3 x 3 block holds each digit exactly once, keeping the digits
    already given."""
    given = instance["input_grid"]  # given[r][c]: the digit printed in row r, column c, if any
    n = len(given)                  # side of the grid: 9
    box = math.isqrt(n)             # side of a block: 3

    model = cp_model.CpModel()

    # grid[r][c] is the digit in row r, column c
    grid = [[model.new_int_var(1, n, f"grid_{r}_{c}") for c in range(n)] for r in range(n)]

    # The given digits stay where they are.
    for r in range(n):
        for c in range(n):
            if given[r][c] != 0:
                model.add(grid[r][c] == given[r][c])

    # Every row holds each digit once.
    for r in range(n):
        model.add_all_different(grid[r])
    # Every column holds each digit once.
    for c in range(n):
        model.add_all_different([grid[r][c] for r in range(n)])
    # Every block holds each digit once.
    for i in range(0, n, box):
        for j in range(0, n, box):
            model.add_all_different([grid[r][c] for r in range(i, i + box) for c in range(j, j + box)])

    return model, {"grid": grid}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
