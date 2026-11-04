# sudoku: a cvc5 (Python) model from DCP Rosetta.
# Download the `sudoku.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/sudoku.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python sudoku.py sudoku.json

from math import isqrt

import cvc5.pythonic as c5


def create_model(instance):
    """Fill a 9 x 9 grid with the digits 1 to 9 so that every row, every column and
    every 3 x 3 block holds each digit exactly once, keeping the digits already given."""
    given = instance["input_grid"]  # given[r][c]: the digit printed in row r, column c, or 0 when the cell is empty
    n = len(given)                  # side of the grid: 9
    box = isqrt(n)                  # side of a block: 3

    # grid[r][c] is the digit in row r, column c
    grid = [[c5.Int(f"grid_{r}_{c}") for c in range(n)] for r in range(n)]

    solver = c5.Solver()

    # Each cell holds a digit from 1 to 9.
    solver.add([grid[r][c] >= 1 for r in range(n) for c in range(n)])
    solver.add([grid[r][c] <= n for r in range(n) for c in range(n)])

    # Every row holds each digit once.
    solver.add([c5.Distinct(row) for row in grid])

    # Every column holds each digit once.
    solver.add([c5.Distinct([grid[r][c] for r in range(n)]) for c in range(n)])

    # Every block holds each digit once.
    for i in range(0, n, box):
        for j in range(0, n, box):
            solver.add(c5.Distinct([grid[r][c] for r in range(i, i + box) for c in range(j, j + box)]))

    # The digits that are given stay where they are.
    solver.add([grid[r][c] == given[r][c] for r in range(n) for c in range(n) if given[r][c] != 0])

    return solver, {"grid": grid}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
