# csplib_057_killer_sudoku: an Exact (Python) model from DCP Rosetta.
# Download the `csplib_057_killer_sudoku.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_057_killer_sudoku.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python csplib_057_killer_sudoku.py csplib_057_killer_sudoku.json

from math import isqrt

from exact import Exact


def create_model(instance):
    """Fill the grid of a killer sudoku with the digits 1 to n so that every row, column
    and box holds each digit once, and every cage (a group of cells) holds distinct
    digits adding up to the total printed in its corner."""
    size = instance["n"]         # side of the grid, which holds the digits 1 to size
    cages = instance["problem"]  # the cages: each has its total and the cells it covers
    box = isqrt(size)            # side of a box

    solver = Exact()

    # Exact identifies its variables by name.
    # x[r][c] is the digit in the cell at row r, column c
    x = [[f"x_{r}_{c}" for c in range(size)] for r in range(size)]
    # digit[r][c][d] is 1 when the cell at row r, column c holds the digit d, and 0 when not
    digit = [[{} for _ in range(size)] for _ in range(size)]
    for r in range(size):
        for c in range(size):
            solver.addVariable(x[r][c], 1, size)
            for d in range(1, size + 1):
                digit[r][c][d] = f"digit_{r}_{c}_{d}"
                solver.addVariable(digit[r][c][d], 0, 1)

    def at_most_once_each(cells):
        """Make the given cells hold no digit twice."""
        for d in range(1, size + 1):
            solver.addConstraint([(1, digit[r][c][d]) for r, c in cells], False, 0, True, 1)

    # Each cell holds exactly one digit, and that digit is its value in x.
    for r in range(size):
        for c in range(size):
            solver.addConstraint([(1, digit[r][c][d]) for d in range(1, size + 1)], True, 1, True, 1)
            solver.addConstraint([(d, digit[r][c][d]) for d in range(1, size + 1)] + [(-1, x[r][c])],
                                 True, 0, True, 0)

    # Each row, column and box holds each digit once.
    for i in range(size):
        at_most_once_each([(i, c) for c in range(size)])
        at_most_once_each([(r, i) for r in range(size)])
    for i in range(box):
        for j in range(box):
            at_most_once_each([(r, c) for r in range(i * box, (i + 1) * box)
                               for c in range(j * box, (j + 1) * box)])

    # Each cage adds up to its total and holds no digit twice.
    for total, cells in cages:
        cage = [(r - 1, c - 1) for r, c in cells]  # the cells of the cage, counted from 0
        solver.addConstraint([(1, x[r][c]) for r, c in cage], True, total, True, total)
        at_most_once_each(cage)

    return solver, {"x": x}


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
