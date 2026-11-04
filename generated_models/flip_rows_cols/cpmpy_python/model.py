# flip_rows_cols: a CPMpy model from DCP Rosetta.
# Download the `flip_rows_cols.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/flip_rows_cols.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python flip_rows_cols.py flip_rows_cols.json

import cpmpy as cp
import numpy as np


def create_model(instance):
    """Flip the sign of whole rows and columns of a number matrix: choose a sign (+1 or -1)
    for every row and every column, and multiply each entry by its row sign and its column
    sign. Every row and every column of the flipped matrix must sum to zero or more, and the
    total sum of the flipped matrix must be as small as possible."""
    matrix = np.array(instance["input_matrix"])  # matrix[i][j]: the number in row i, column j
    rows, cols = matrix.shape

    # A flipped entry keeps its absolute value, so it lies within -max_abs..max_abs.
    max_abs = int(np.abs(matrix).max())

    # row_signs[i] and col_signs[j] are the sign chosen for row i and column j.
    # The domain -1..1 is used and 0 is excluded below.
    row_signs = cp.intvar(-1, 1, shape=rows, name="row_signs")
    col_signs = cp.intvar(-1, 1, shape=cols, name="col_signs")

    # x[i, j] is the entry (i, j) after flipping.
    x = cp.intvar(-max_abs, max_abs, shape=(rows, cols), name="x")

    model = cp.Model()

    # A sign is -1 or +1, never 0.
    model.add(row_signs != 0)
    model.add(col_signs != 0)

    # The flipped entry is the original entry times its row sign times its column sign.
    for i in range(rows):
        model.add(x[i, :] == matrix[i, :] * row_signs[i] * col_signs)

    # Every flipped row and every flipped column sums to zero or more.
    model.add(x.sum(axis=1) >= 0)
    model.add(x.sum(axis=0) >= 0)

    # Find the flip with the smallest total sum.
    model.minimize(cp.sum(x))

    return model, {"row_signs": row_signs, "col_signs": col_signs}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
