# csplib_057_killer_sudoku: a SCIP (Python) model from DCP Rosetta.
# Download the `csplib_057_killer_sudoku.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_057_killer_sudoku.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python csplib_057_killer_sudoku.py csplib_057_killer_sudoku.json

import numpy as np
from pyscipopt import Model, quicksum


def create_model(instance):
    """Killer sudoku: fill an n x n grid with the digits 1 to n so that every row,
    every column and every nonet (3 x 3 block) holds each digit exactly once, and
    every cage (a group of cells) sums to the small number printed in its corner,
    with no digit repeated inside a cage. There is no objective: any grid that
    follows these rules is a solution."""
    n = instance["n"]  # the grid side, and the largest digit (the statement's grid is 9 x 9)
    cages = instance["problem"]  # cages[k] = [target sum, [[row, column], ...]], 1-based rows and columns
    box = 3  # the nonet side: the statement's 9 x 9 grid has nine 3 x 3 nonets, a fixed rule, not from the instance

    model = Model("killer_sudoku")

    # b[r, c, d] = 1 when cell (r, c) holds digit d + 1, and 0 when not.
    # SCIP has no all-different constraint, so the sudoku and cage rules are written
    # over these one-hot binaries: each digit is counted once per row, column, nonet and cage.
    b = model.addMatrixVar((n, n, n), vtype="B", name="b")
    digits = np.arange(1, n + 1)

    # Each cell holds exactly one digit.
    model.addMatrixCons(b.sum(axis=2) == 1)

    # x[r, c] is the digit in cell (r, c): the one digit whose bit is set. Its values lie
    # in 1 to n because each cell takes exactly one of the n one-hot digits.
    x = (digits * b).sum(axis=2)

    # Each row holds each digit exactly once.
    model.addMatrixCons(b.sum(axis=1) == 1)

    # Each column holds each digit exactly once.
    model.addMatrixCons(b.sum(axis=0) == 1)

    # Each nonet holds each digit exactly once.
    for top in range(0, n, box):
        for left in range(0, n, box):
            model.addMatrixCons(b[top:top + box, left:left + box].sum(axis=(0, 1)) == 1)

    for target, cells in cages:
        # Cell positions in the data are 1-based; shift them to 0-based indexes.
        cage_cells = [(r - 1, c - 1) for r, c in cells]

        # The digits in the cage sum to the target printed in its corner.
        model.addCons(quicksum(x[r, c] for r, c in cage_cells) == target)

        # No digit appears twice in the cage.
        for d in range(n):
            model.addCons(quicksum(b[r, c, d] for r, c in cage_cells) <= 1)

    return model, {"x": x}


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
