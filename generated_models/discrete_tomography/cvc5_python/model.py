# discrete_tomography: a cvc5 (Python) model from DCP Rosetta.
# Download the `discrete_tomography.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/discrete_tomography.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python discrete_tomography.py discrete_tomography.json

import cvc5.pythonic as c5


def create_model(instance):
    """A matrix of zeroes and ones is "x-rayed" vertically and horizontally,
    giving the number of ones in each row and column. Reconstruct the matrix."""
    row_sums = instance["row_sums"]  # row_sums[i]: the number of ones in row i
    col_sums = instance["col_sums"]  # col_sums[j]: the number of ones in column j

    # matrix[i][j] is the value of the cell in row i, column j
    matrix = [[c5.Int(f"matrix_{i}_{j}") for j in range(len(col_sums))] for i in range(len(row_sums))]

    solver = c5.Solver()

    # Each cell holds 0 or 1.
    solver.add([c5.And(cell >= 0, cell <= 1) for row in matrix for cell in row])

    # Each row contains the given number of ones.
    solver.add([c5.Sum(row) == total for row, total in zip(matrix, row_sums)])

    # Each column contains the given number of ones.
    solver.add([c5.Sum([row[j] for row in matrix]) == total for j, total in enumerate(col_sums)])

    return solver, {"matrix": matrix}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
