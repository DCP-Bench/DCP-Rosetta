# sudoku: a CPMpy model from DCP Rosetta.
# Download the `sudoku.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/sudoku.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python sudoku.py sudoku.json

from math import isqrt

import cpmpy as cp


def create_model(instance):
    """Complete a partly filled Sudoku grid so that each row, column and block
    holds every digit from 1 to n exactly once."""
    given = instance["input_grid"]  # given[i][j]: the digit in row i, column j, or 0 when the cell is empty
    n = len(given)                  # side of the grid: 9 for a standard Sudoku
    box = isqrt(n)                  # side of a block: 3 for a standard Sudoku

    # grid[i, j] is the digit in row i, column j
    grid = cp.intvar(1, n, shape=(n, n), name="grid")

    model = cp.Model()

    # The digits that are given stay where they are.
    for i in range(n):
        for j in range(n):
            if given[i][j] != 0:
                model.add(grid[i, j] == given[i][j])

    # Every row holds each digit once.
    model.add([cp.AllDifferent(row) for row in grid])

    # Every column holds each digit once.
    model.add([cp.AllDifferent(col) for col in grid.T])

    # Every block holds each digit once.
    for i in range(0, n, box):
        for j in range(0, n, box):
            model.add(cp.AllDifferent(grid[i:i + box, j:j + box]))

    return model, {"grid": grid}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
