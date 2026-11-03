# csplib_057_killer_sudoku: a Z3 (Python) model from DCP Rosetta.
# Download the `csplib_057_killer_sudoku.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_057_killer_sudoku.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python csplib_057_killer_sudoku.py csplib_057_killer_sudoku.json

from math import isqrt

import z3


def create_model(instance):
    """Fill an n-by-n grid with the numbers 1 to n so that every row, column and box
    holds each number once, and every cage (a group of cells) holds distinct numbers
    adding up to the small number printed in its corner."""
    n = instance["n"]            # side of the grid
    cages = instance["problem"]  # each cage is [total, cells], with cells as (row, column) pairs
    box = isqrt(n)               # side of a box

    # x[r][c] is the number in row r, column c
    x = [[z3.Int(f"x_{r}_{c}") for c in range(n)] for r in range(n)]

    solver = z3.Solver()

    # Every cell holds a number from 1 to n.
    for r in range(n):
        for c in range(n):
            solver.add(x[r][c] >= 1, x[r][c] <= n)

    # Every row holds each number once.
    for r in range(n):
        solver.add(z3.Distinct(x[r]))
    # Every column holds each number once.
    for c in range(n):
        solver.add(z3.Distinct([x[r][c] for r in range(n)]))
    # Every box holds each number once.
    for i in range(box):
        for j in range(box):
            solver.add(z3.Distinct([x[r][c]
                                    for r in range(i * box, (i + 1) * box)
                                    for c in range(j * box, (j + 1) * box)]))

    # Each cage adds up to its total and holds no number twice. Cells are counted
    # from 1, as in the puzzle.
    for total, cells in cages:
        cage = [x[r - 1][c - 1] for r, c in cells]
        solver.add(z3.Sum(cage) == total)
        solver.add(z3.Distinct(cage))

    return solver, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
