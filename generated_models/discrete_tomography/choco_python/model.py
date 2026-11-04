# discrete_tomography: a Choco-solver (Python) model from DCP Rosetta.
# Download the `discrete_tomography.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/discrete_tomography.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python discrete_tomography.py discrete_tomography.json

from pychoco.model import Model


def create_model(instance):
    """A matrix of zeroes and ones is "x-rayed" vertically and horizontally,
    giving the number of ones in each row and column. Reconstruct the matrix."""
    row_sums = instance["row_sums"]  # row_sums[i]: the number of ones in row i
    col_sums = instance["col_sums"]  # col_sums[j]: the number of ones in column j
    n_rows = len(row_sums)           # the number of rows
    n_cols = len(col_sums)           # the number of columns

    model = Model()

    # matrix[i][j] is 1 when the cell in row i, column j holds a one, and 0 otherwise
    matrix = [[model.intvar(0, 1, name=f"matrix_{i}_{j}") for j in range(n_cols)]
              for i in range(n_rows)]

    # Each row contains the given number of ones.
    for i in range(n_rows):
        model.sum(matrix[i], "=", row_sums[i]).post()
    # Each column contains the given number of ones.
    for j in range(n_cols):
        model.sum([matrix[i][j] for i in range(n_rows)], "=", col_sums[j]).post()

    return model, {"matrix": matrix}, None


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
