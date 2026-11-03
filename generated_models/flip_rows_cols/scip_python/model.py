# flip_rows_cols: a SCIP (Python) model from DCP Rosetta.
# Download the `flip_rows_cols.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/flip_rows_cols.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python flip_rows_cols.py flip_rows_cols.json

import numpy as np
from pyscipopt import Model


def create_model(instance):
    """Flip the sign of whole rows and whole columns of a matrix so that every
    row and every column sums to a positive number or zero, and the sum of all
    entries is as small as possible. Output the row signs and the column signs,
    each -1 or 1."""
    # matrix[i][j]: the number in row i, column j of the input matrix (instance field input_matrix)
    matrix = np.array(instance["input_matrix"])
    # the number of rows and columns comes from the shape of that matrix, so it differs per instance
    n_rows, n_cols = matrix.shape

    model = Model("flip_rows_cols")

    # row_flip[i] is 1 when row i has its sign flipped, and 0 when not
    row_flip = model.addMatrixVar((n_rows,), vtype="B", name="row_flip")
    # col_flip[j] is 1 when column j has its sign flipped, and 0 when not
    col_flip = model.addMatrixVar((n_cols,), vtype="B", name="col_flip")
    # cell_flip[i, j] is 1 when entry (i, j) ends up negated overall, which
    # happens exactly when one of its row and its column is flipped, but not both
    cell_flip = model.addMatrixVar((n_rows, n_cols), vtype="B", name="cell_flip")

    # Entry (i, j) keeps its sign when both its row and its column are flipped, or neither.
    # SCIP has no matrix form of exclusive or, so each entry gets one xor constraint:
    # row_flip + col_flip + cell_flip is even, which makes cell_flip the exclusive or of the other two
    for i, j in np.ndindex(n_rows, n_cols):
        model.addConsXor([row_flip[i], col_flip[j], cell_flip[i, j]], False)

    # The entries after flipping: matrix[i][j] keeps its sign when cell_flip is 0, and is negated when it is 1
    flipped = matrix * (1 - 2 * cell_flip)

    # Each row of the flipped matrix sums to a positive number or zero
    model.addMatrixCons(flipped.sum(axis=1) >= 0)
    # Each column of the flipped matrix sums to a positive number or zero
    model.addMatrixCons(flipped.sum(axis=0) >= 0)

    # The overall sum of the flipped matrix is as small as possible
    model.setObjective(flipped.sum(), "minimize")

    # the output signs: 1 - 2 * flip gives 1 when not flipped and -1 when flipped
    outputs = {"row_signs": 1 - 2 * row_flip, "col_signs": 1 - 2 * col_flip}
    return model, outputs


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
