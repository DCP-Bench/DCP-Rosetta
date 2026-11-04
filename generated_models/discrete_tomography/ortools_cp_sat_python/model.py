# discrete_tomography: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `discrete_tomography.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/discrete_tomography.html
# Then run it on the first instance (after `pip install ortools`):
#   python discrete_tomography.py discrete_tomography.json

from ortools.sat.python import cp_model


def create_model(instance):
    """A matrix of zeroes and ones is "x-rayed" vertically and horizontally,
    giving the number of ones in each row and column. Reconstruct the matrix."""
    row_sums = instance["row_sums"]  # row_sums[i]: the number of ones in row i
    col_sums = instance["col_sums"]  # col_sums[j]: the number of ones in column j

    model = cp_model.CpModel()

    # matrix[i][j] is 1 when the cell in row i, column j holds a one, and 0 otherwise
    matrix = [
        [model.new_int_var(0, 1, f"matrix_{i}_{j}") for j in range(len(col_sums))]
        for i in range(len(row_sums))
    ]

    # Each row contains the given number of ones.
    for row, total in zip(matrix, row_sums):
        model.add(sum(row) == total)
    # Each column contains the given number of ones.
    for j, total in enumerate(col_sums):
        model.add(sum(row[j] for row in matrix) == total)

    return model, {"matrix": matrix}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
