# sudoku: a SCIP (Python) model from DCP Rosetta.
# Download the `sudoku.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/sudoku.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python sudoku.py sudoku.json

from math import isqrt

from pyscipopt import Model, quicksum


def create_model(instance):
    """Sudoku: fill a square grid with digits so that every row, every column and
    every box of the grid contains each digit exactly once. Some cells are given;
    the empty ones must be filled. The usual grid is 9 x 9 with boxes of 3 x 3."""
    givens = instance["input_grid"]  # givens[r][c]: the digit given in cell (r, c), 0 when the cell is empty
    n = len(givens)                  # the side of the grid, taken from the instance (9 for the usual sudoku)
    box = isqrt(n)                   # the side of one box (3 for a 9 x 9 grid)
    digits = range(1, n + 1)         # the digits allowed in a cell: 1 to n, from the sudoku rules
    cells = [(r, c) for r in range(n) for c in range(n)]

    model = Model("sudoku")

    # grid[r, c] is the digit in cell (r, c); its bounds 1 and n are the digits allowed
    grid = model.addMatrixVar((n, n), vtype="I", lb=1, ub=n, name="grid")

    # place[r, c, v] is 1 when cell (r, c) holds digit v, and 0 when not.
    # The one-hot binaries make "each digit once" a sum of binaries, which is much
    # stronger for the solver than pairwise "not equal" constraints.
    place = {(r, c, v): model.addVar(f"place_{r}_{c}_{v}", vtype="B") for (r, c) in cells for v in digits}

    # Each cell holds exactly one digit.
    for r, c in cells:
        model.addCons(quicksum(place[r, c, v] for v in digits) == 1)

    # The digit of a cell is the digit its one-hot choice selects.
    for r, c in cells:
        model.addCons(grid[r, c] == quicksum(v * place[r, c, v] for v in digits))

    # Each row contains each digit once.
    for r in range(n):
        for v in digits:
            model.addCons(quicksum(place[r, c, v] for c in range(n)) == 1)

    # Each column contains each digit once.
    for c in range(n):
        for v in digits:
            model.addCons(quicksum(place[r, c, v] for r in range(n)) == 1)

    # Each box contains each digit once. The boxes are the box x box blocks of the grid.
    for top in range(0, n, box):
        for left in range(0, n, box):
            block = [(r, c) for r in range(top, top + box) for c in range(left, left + box)]
            for v in digits:
                model.addCons(quicksum(place[r, c, v] for r, c in block) == 1)

    # The given digits are fixed: the cell holds that digit. Empty cells (0) are left open.
    for r, c in cells:
        if givens[r][c] != 0:
            model.addCons(place[r, c, givens[r][c]] == 1)

    # No objective: any grid that obeys the rules is an answer (a satisfaction problem).
    return model, {"grid": grid}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
