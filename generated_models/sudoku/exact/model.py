# sudoku: an Exact (Python) model from DCP Rosetta.
# Download the `sudoku.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/sudoku.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python sudoku.py sudoku.json

import math

from exact import Exact


def create_model(instance):
    """Sudoku: fill an n x n grid with the digits 1 to n so that every row, every column and every
    section holds each digit exactly once, keeping the digits already given."""
    given = instance["input_grid"]  # given[r][c] is the digit in row r, column c, or 0 when the cell is empty
    n = len(given)                  # the grid has n rows and n columns
    box = math.isqrt(n)             # the side of a section: the square root of n, 3 for the 9 x 9 grid

    solver = Exact()

    # Exact identifies its variables by name.
    # grid[r][c] is the digit in row r, column c
    grid = [[f"grid_{r}_{c}" for c in range(n)] for r in range(n)]
    # holds[r][c][d] is 1 when cell (r, c) holds digit d, and 0 when not
    holds = [[{} for _ in range(n)] for _ in range(n)]
    for r in range(n):
        for c in range(n):
            solver.addVariable(grid[r][c], 1, n)
            for d in range(1, n + 1):
                holds[r][c][d] = f"holds_{r}_{c}_{d}"
                solver.addVariable(holds[r][c][d], 0, 1)

    def each_digit_once(cells):
        """Each digit from 1 to n is held by exactly one of the cells."""
        for d in range(1, n + 1):
            solver.addConstraint([(1, holds[r][c][d]) for r, c in cells], True, 1, True, 1)

    for r in range(n):
        for c in range(n):
            # Each cell holds exactly one digit.
            solver.addConstraint([(1, holds[r][c][d]) for d in range(1, n + 1)], True, 1, True, 1)
            # The entry in the grid is the digit the cell holds.
            solver.addConstraint([(d, holds[r][c][d]) for d in range(1, n + 1)] + [(-1, grid[r][c])],
                                 True, 0, True, 0)
            # Each digit given in the puzzle stays in its cell.
            if given[r][c] != 0:
                solver.addConstraint([(1, holds[r][c][given[r][c]])], True, 1, True, 1)

    # Each row holds each digit once.
    for i in range(n):
        each_digit_once([(i, c) for c in range(n)])
    # Each column holds each digit once.
    for i in range(n):
        each_digit_once([(r, i) for r in range(n)])
    # Each section holds each digit once.
    for i in range(0, n, box):
        for j in range(0, n, box):
            each_digit_once([(r, c) for r in range(i, i + box) for c in range(j, j + box)])

    return solver, {"grid": grid}


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
