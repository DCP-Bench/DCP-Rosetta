# discrete_tomography: a Z3 (Python) model from DCP Rosetta.
# Download the `discrete_tomography.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/discrete_tomography.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python discrete_tomography.py discrete_tomography.json

import z3


def create_model(instance):
    """A matrix of zeroes and ones is x-rayed by rows and columns, giving the number
    of ones in each row and column. Reconstruct the matrix."""
    row_sums = instance["row_sums"]  # row_sums[i]: the number of ones in row i
    col_sums = instance["col_sums"]  # col_sums[j]: the number of ones in column j
    n_rows, n_columns = len(row_sums), len(col_sums)  # the size of the matrix

    # matrix[i][j] is the cell in row i, column j: 1 if it holds a one, 0 otherwise
    matrix = [[z3.Int(f"x_{i}_{j}") for j in range(n_columns)] for i in range(n_rows)]

    solver = z3.Solver()

    # Each cell holds either a zero or a one.
    solver.add([z3.And(cell >= 0, cell <= 1) for row in matrix for cell in row])

    # Each row has as many ones as its row sum.
    solver.add([z3.Sum(matrix[i]) == row_sums[i] for i in range(n_rows)])

    # Each column has as many ones as its column sum.
    solver.add([z3.Sum([matrix[i][j] for i in range(n_rows)]) == col_sums[j] for j in range(n_columns)])

    return solver, {"matrix": matrix}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
