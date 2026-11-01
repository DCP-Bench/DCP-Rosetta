# discrete_tomography: a CPMpy model from DCP Rosetta.
# Download the `discrete_tomography.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/discrete_tomography.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python discrete_tomography.py discrete_tomography.json

import cpmpy as cp


def create_model(instance):
    """A matrix of zeroes and ones is "x-rayed" vertically and horizontally,
    giving the number of ones in each row and column. Reconstruct the matrix."""
    row_sums = instance["row_sums"]  # row_sums[i]: the number of ones in row i
    col_sums = instance["col_sums"]  # col_sums[j]: the number of ones in column j

    # matrix[i, j] is the value (0 or 1) of the cell in row i, column j
    matrix = cp.intvar(0, 1, shape=(len(row_sums), len(col_sums)), name="matrix")

    model = cp.Model()
    # Each row contains the given number of ones.
    model.add(matrix.sum(axis=1) == row_sums)
    # Each column contains the given number of ones.
    model.add(matrix.sum(axis=0) == col_sums)

    return model, {"matrix": matrix}


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
