# session1_magic_square: a SCIP (Python) model from DCP Rosetta.
# Download the `session1_magic_square.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_magic_square.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python session1_magic_square.py session1_magic_square.json

import numpy as np
from pyscipopt import SCIP_PARAMEMPHASIS, Model


def create_model(instance):
    """Fill an n x n grid with the numbers 1 to n*n, each used once, so that
    every row, every column and both diagonals add up to the same total
    n(n^2+1)/2. The statement excludes n = 2, which has no such square."""
    n = instance["n"]  # the side of the square, from the instance
    cells = n * n      # the number of cells; the numbers used are 1 to cells

    # The common total of each row, column and diagonal, from the statement's
    # formula n(n^2+1)/2. It is an integer for every n: n(n^2+1) is even.
    total = n * (cells + 1) // 2

    model = Model("session1_magic_square")

    # SCIP's default settings are slow to find a first square for larger n. The
    # feasibility emphasis speeds up the search for a solution and does not change
    # which squares exist.
    model.setEmphasis(SCIP_PARAMEMPHASIS.FEASIBILITY)

    # value[i, j, v] is 1 when cell (i, j) holds the number v + 1, and 0 when
    # not (rows, columns and choices are 0-based). The cell's number is chosen
    # this way (one-hot) because SCIP has no all-different constraint, so
    # distinctness is written with the constraint below.
    value = model.addMatrixVar((n, n, cells), vtype="B", name="value")

    # Each cell holds exactly one number.
    model.addMatrixCons(value.sum(axis=2) == 1)

    # Each number is in at most one cell (the all-different of the statement).
    # There are as many numbers as cells, so every number is used exactly once.
    model.addMatrixCons(value.sum(axis=(0, 1)) <= 1)

    # square[i, j] is the number in cell (i, j): the sum of the numbers v + 1
    # weighted by the choice value[i, j, v]. This expression is the output.
    numbers = np.arange(1, cells + 1)
    square = (value * numbers).sum(axis=2)

    # Every row adds up to the total.
    model.addMatrixCons(square.sum(axis=1) == total)

    # Every column adds up to the total.
    model.addMatrixCons(square.sum(axis=0) == total)

    # The main diagonal (top left to bottom right) adds up to the total. The
    # mask is 1 on the diagonal cells and 0 elsewhere.
    diagonal = np.eye(n, dtype=int)
    model.addCons((square * diagonal).sum() == total)

    # The other diagonal (top right to bottom left) adds up to the total. The
    # mask is the main diagonal's mask with its columns reversed.
    anti_diagonal = np.fliplr(diagonal)
    model.addCons((square * anti_diagonal).sum() == total)

    return model, {"square": square}


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
