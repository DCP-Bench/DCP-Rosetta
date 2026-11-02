# csplib_057_killer_sudoku: a cvc5 (Python) model from DCP Rosetta.
# Download the `csplib_057_killer_sudoku.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_057_killer_sudoku.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python csplib_057_killer_sudoku.py csplib_057_killer_sudoku.json

from math import isqrt

import cvc5.pythonic as c5


def at_most_one(conditions):
    # No two of the conditions hold together.
    return [c5.Or(c5.Not(a), c5.Not(b)) for i, a in enumerate(conditions) for b in conditions[i + 1:]]


def exactly_one(conditions):
    # Exactly one of the conditions holds.
    return [c5.Or(conditions)] + at_most_one(conditions)


def create_model(instance):
    """Fill an n by n grid with the numbers 1 to n so that every row, column and nonet
    holds each number once, and every cage (a group of cells) holds distinct numbers
    that add up to the small number printed in its corner."""
    n = instance["n"]            # side of the grid
    cages = instance["problem"]  # cages[c] = [total, cells]: the total of cage c and its cells
    box = isqrt(n)               # side of a nonet (3 for the usual 9 by 9 grid)

    # p[r][c][k] is true when the cell in row r, column c holds the number k + 1
    p = [[[c5.Bool(f"p_{r}_{c}_{k}") for k in range(n)] for c in range(n)] for r in range(n)]
    # x[r][c] is the number in row r, column c of the grid, counted from 0
    x = [[c5.Int(f"x_{r}_{c}") for c in range(n)] for r in range(n)]

    solver = c5.Solver()

    # Each cell holds exactly one number from 1 to n, and x gives that number.
    for r in range(n):
        for c in range(n):
            solver.add(exactly_one(p[r][c]))
            solver.add(x[r][c] == c5.Sum([c5.If(p[r][c][k], k + 1, 0) for k in range(n)]))

    # The rows, columns and nonets, each as a list of cells.
    units = []
    for r in range(n):
        units.append([(r, c) for c in range(n)])
        units.append([(k, r) for k in range(n)])
    if box * box == n:
        for i in range(box):
            for j in range(box):
                units.append([(i * box + a, j * box + b) for a in range(box) for b in range(box)])

    # Each row, column and nonet holds each number once.
    for unit in units:
        for k in range(n):
            solver.add(exactly_one([p[r][c][k] for r, c in unit]))

    # Cage cells are given with rows and columns counted from 1, as in the puzzle.
    for total, cells in cages:
        cage = [(r - 1, c - 1) for r, c in cells]
        # The numbers in the cage add up to its total.
        solver.add(c5.Sum([x[r][c] for r, c in cage]) == total)
        # No number repeats inside the cage.
        if len(cage) > 1:
            for k in range(n):
                solver.add(at_most_one([p[r][c][k] for r, c in cage]))

    return solver, {"x": x}


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
