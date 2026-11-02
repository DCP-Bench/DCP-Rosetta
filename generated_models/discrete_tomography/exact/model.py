# discrete_tomography: an Exact (Python) model from DCP Rosetta.
# Download the `discrete_tomography.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/discrete_tomography.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python discrete_tomography.py discrete_tomography.json

from exact import Exact


def create_model(instance):
    """A matrix of zeroes and ones is x-rayed vertically and horizontally, giving
    the number of ones in each row and each column. Reconstruct the matrix."""
    row_sums = instance["row_sums"]  # row_sums[i]: the number of ones in row i
    col_sums = instance["col_sums"]  # col_sums[j]: the number of ones in column j
    n_rows = len(row_sums)           # the number of rows
    n_cols = len(col_sums)           # the number of columns

    solver = Exact()

    # Exact identifies its variables by name.
    # matrix[i][j] is 1 when the cell in row i, column j holds a one, and 0 when it holds a zero
    matrix = [[f"m{i}_{j}" for j in range(n_cols)] for i in range(n_rows)]
    for row in matrix:
        for name in row:
            solver.addVariable(name, 0, 1)

    # Each row contains the given number of ones.
    for i in range(n_rows):
        solver.addConstraint([(1, name) for name in matrix[i]], True, row_sums[i], True, row_sums[i])

    # Each column contains the given number of ones.
    for j in range(n_cols):
        solver.addConstraint([(1, matrix[i][j]) for i in range(n_rows)], True, col_sums[j], True, col_sums[j])

    return solver, {"matrix": matrix}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
