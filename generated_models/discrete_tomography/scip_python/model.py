# discrete_tomography: a SCIP (Python) model from DCP Rosetta.
# Download the `discrete_tomography.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/discrete_tomography.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python discrete_tomography.py discrete_tomography.json

from pyscipopt import Model


def create_model(instance):
    """Discrete tomography: reconstruct a matrix of zeroes and ones from its
    X-rays. The matrix is X-rayed vertically and horizontally, which gives the
    number of ones in each row and in each column; find a matrix with those
    totals."""
    row_sums = instance["row_sums"]  # row_sums[i]: the number of ones in row i
    col_sums = instance["col_sums"]  # col_sums[j]: the number of ones in column j
    rows = len(row_sums)  # the matrix has one row per row sum
    cols = len(col_sums)  # and one column per column sum

    model = Model("discrete_tomography")

    # x[i, j] is 1 when cell (i, j) of the matrix holds a one, and 0 when it holds a zero
    # (the matrix holds only zeroes and ones, so each cell is binary)
    x = model.addMatrixVar((rows, cols), vtype="B", name="x")

    # Each row contains exactly as many ones as its row sum.
    model.addMatrixCons(x.sum(axis=1) == row_sums)

    # Each column contains exactly as many ones as its column sum.
    model.addMatrixCons(x.sum(axis=0) == col_sums)

    # The problem has no objective: any matrix that meets all the row and column
    # sums is a solution.
    return model, {"matrix": x}


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
