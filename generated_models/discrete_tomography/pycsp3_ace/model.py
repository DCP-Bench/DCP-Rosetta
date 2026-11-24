# discrete_tomography: a PyCSP3 model from DCP Rosetta.
# Download the `discrete_tomography.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/discrete_tomography.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python discrete_tomography.py discrete_tomography.json

from pycsp3 import *


def create_model(instance):
    """A matrix which contains zeroes and ones gets "x-rayed" vertically and horizontally,
    giving the total number of ones in each row and column. The problem is to reconstruct
    the contents of the matrix from this information."""
    row_sums = instance["row_sums"]  # row_sums[i]: the total number of ones in row i
    col_sums = instance["col_sums"]  # col_sums[j]: the total number of ones in column j
    n_rows = len(row_sums)
    n_cols = len(col_sums)

    # matrix[i][j] is 1 when the cell in row i and column j holds a one, 0 otherwise
    matrix = VarArray(size=[n_rows, n_cols], dom={0, 1})

    satisfy(
        # Each row contains as many ones as its row sum.
        (Sum(matrix[i]) == row_sums[i] for i in range(n_rows)),
        # Each column contains as many ones as its column sum.
        (Sum(matrix[:, j]) == col_sums[j] for j in range(n_cols)),
    )

    return {"matrix": matrix}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        print("matrix", "=")
        for row in outputs["matrix"]:
            print(values(row))
    else:
        print("No solution:", status())
