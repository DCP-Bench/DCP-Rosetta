# csplib_054_n_queens: a SCIP (Python) model from DCP Rosetta.
# Download the `csplib_054_n_queens.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_054_n_queens.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python csplib_054_n_queens.py csplib_054_n_queens.json

from pyscipopt import Model, quicksum


def create_model(instance):
    """Place n queens on an n x n chessboard so that no two queens share a row,
    a column or a diagonal. The output queens[i] is the column, numbered 1 to n,
    of the queen in row i + 1.

    The only instance field is n, the side of the board. It is also the number
    of queens, so every row and every column holds exactly one queen."""
    n = instance["n"]  # n: the board is n x n and holds n queens

    model = Model("n_queens")

    # q[r, c] is 1 when a queen stands on row r, column c (both 0-based), and 0 otherwise.
    # SCIP has no all-different constraint, so each row's queen position is a one-hot
    # row of binaries instead of one integer per row.
    q = model.addMatrixVar((n, n), vtype="B", name="q")

    # Each row holds exactly one queen, so no two queens share a row.
    model.addMatrixCons(q.sum(axis=1) == 1)

    # Each column holds exactly one queen, so no two queens share a column.
    model.addMatrixCons(q.sum(axis=0) == 1)

    # The diagonals are not rows or columns of the matrix, so they are posted one by one.
    # Diagonal d of the first kind holds the squares with r + c == d (d from 0 to 2n - 2);
    # diagonal d of the second kind holds the squares with r - c == d (d from -(n - 1) to n - 1).
    # Each diagonal holds at most one queen, so no two queens share a diagonal.
    for d in range(2 * n - 1):
        model.addCons(quicksum(q[r, d - r] for r in range(n) if 0 <= d - r < n) <= 1)
    for d in range(-(n - 1), n):
        model.addCons(quicksum(q[r, r - d] for r in range(n) if 0 <= r - d < n) <= 1)

    # queens[i] is the column of the queen in row i + 1; columns are numbered from 1,
    # as the statement asks, so the weight of column c (0-based) is c + 1.
    # Each row's sum has exactly one term equal to 1, so it is the queen's column.
    queens = [quicksum((c + 1) * q[r, c] for c in range(n)) for r in range(n)]

    return model, {"queens": queens}


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
