# discrete_tomography: a Python-MIP (Python) model from DCP Rosetta.
# Download the `discrete_tomography.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/discrete_tomography.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python discrete_tomography.py discrete_tomography.json

import mip


def create_model(instance):
    """A matrix of zeroes and ones is "x-rayed" vertically and horizontally,
    giving the number of ones in each row and column. Reconstruct the matrix."""
    row_sums = instance["row_sums"]  # row_sums[i]: the number of ones in row i
    col_sums = instance["col_sums"]  # col_sums[j]: the number of ones in column j
    n_rows = len(row_sums)           # the number of rows
    n_cols = len(col_sums)           # the number of columns

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # matrix[i][j] is 1 when the cell in row i, column j holds a one, and 0 otherwise
    matrix = [
        [model.add_var(f"matrix_{i}_{j}", var_type=mip.BINARY) for j in range(n_cols)]
        for i in range(n_rows)
    ]

    # Each row has its given number of ones.
    for i in range(n_rows):
        model += mip.xsum(matrix[i][j] for j in range(n_cols)) == row_sums[i]

    # Each column has its given number of ones.
    for j in range(n_cols):
        model += mip.xsum(matrix[i][j] for i in range(n_rows)) == col_sums[j]

    return model, {"matrix": matrix}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
