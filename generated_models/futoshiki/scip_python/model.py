# futoshiki: a SCIP (Python) model from DCP Rosetta.
# Download the `futoshiki.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/futoshiki.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python futoshiki.py futoshiki.json

import numpy as np
from pyscipopt import Model


def create_model(instance):
    """A futoshiki puzzle on an n x n grid, where n is the size of the instance's board: fill every
    cell with a digit from 1 to n so that each row and each column holds every digit
    exactly once, keep the digits already given, and honour every inequality sign
    between two neighbouring cells. The puzzle has no objective; any grid that obeys
    these rules is a solution."""
    values = instance["values"]  # n x n list of the given digits, 0 where the cell is empty
    lt = instance["lt"]  # each [r1, c1, r2, c2] (1-based) says the digit in (r1, c1) is less than the one in (r2, c2)
    n = len(values)  # the board is n x n

    model = Model("futoshiki")

    # one[r, c, d] is 1 when cell (r, c) holds digit d + 1, and 0 otherwise; the digits are 1 to n, as the statement says.
    # SCIP has no all-different constraint, so each digit is counted in every row and column
    # with binaries. A given digit fixes its binary to 1 through the lower bound.
    lb = [[[1 if v == d + 1 else 0 for d in range(n)] for v in row] for row in values]
    one = model.addMatrixVar((n, n, n), vtype="B", lb=lb, name="one")

    # Every cell holds exactly one digit.
    model.addMatrixCons(one.sum(axis=2) == 1)
    # Every row holds each digit exactly once.
    model.addMatrixCons(one.sum(axis=1) == 1)
    # Every column holds each digit exactly once.
    model.addMatrixCons(one.sum(axis=0) == 1)

    # The digit in each cell, the output: the sum of digit * binary over the digits.
    grid = (one * np.arange(1, n + 1)).sum(axis=2)

    # Each inequality sign of the puzzle. The coordinates are 1-based (the data reaches row n),
    # so they are shifted to 0-based indices. SCIP has no strict <, so "less than" is written
    # as "at most one less", which is the same for integers.
    for r1, c1, r2, c2 in lt:
        model.addCons(grid[r1 - 1, c1 - 1] <= grid[r2 - 1, c2 - 1] - 1)

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
