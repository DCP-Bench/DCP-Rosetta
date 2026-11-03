# csplib_057_killer_sudoku: a hermax (Python) model from DCP Rosetta.
# Download the `csplib_057_killer_sudoku.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_057_killer_sudoku.html
# Then run it on the first instance (after `pip install hermax`):
#   python csplib_057_killer_sudoku.py csplib_057_killer_sudoku.json

from math import isqrt

from hermax.model import Model


def create_model(instance):
    """Killer sudoku: fill an n-by-n grid with the digits 1..n so that every row,
    every column and every box holds each digit once, and every cage (a group of
    cells) adds up to its printed target with no digit repeated inside the cage."""
    n = instance["n"]              # side of the grid, 9 for a standard killer sudoku
    cages = instance["problem"]    # cages[k] = [target sum, [[row, column], ...]], rows and columns counted from 1
    box = isqrt(n)                 # side of a box (3 for a 9-by-9 grid)

    m = Model()
    # x[r][c] is the digit in row r, column c (0-based indices), a value from 1 to n
    x = m.int_matrix("x", n, n, 1, n)

    # Each row and each column holds every digit exactly once.
    for i in range(n):
        m &= x.row(i).all_different()
        m &= x.col(i).all_different()

    # Each box holds every digit exactly once.
    for bi in range(box):
        for bj in range(box):
            cells = [x[r][c] for r in range(bi * box, (bi + 1) * box)
                     for c in range(bj * box, (bj + 1) * box)]
            m &= m.vector(cells).all_different()

    # Each cage adds up to its target sum, and no digit repeats inside the cage.
    for target, cage_cells in cages:
        cage = [x[r - 1][c - 1] for r, c in cage_cells]  # the digits of the cells in this cage
        m &= (sum(cage) == target)
        m &= m.vector(cage).all_different()

    # No objective: any grid that meets the rules is a solution.
    return m, {"x": x}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
