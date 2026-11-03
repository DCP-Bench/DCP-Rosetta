# flip_rows_cols: a Choco-solver (Python) model from DCP Rosetta.
# Download the `flip_rows_cols.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/flip_rows_cols.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python flip_rows_cols.py flip_rows_cols.json

from pychoco.model import Model


def create_model(instance):
    """Choose whether to flip the sign of each row and each column of an array
    of positive and negative numbers, so that every row and every column sums
    to a positive number or zero, and the overall sum is as small as possible."""
    matrix = instance["input_matrix"]  # matrix[i][j]: the number in row i and column j
    n_rows = len(matrix)               # the number of rows
    n_cols = len(matrix[0])            # the number of columns

    model = Model()

    # row_signs[i] is -1 when row i is flipped and 1 otherwise
    row_signs = [model.intvar([-1, 1], name=f"row_sign_{i}") for i in range(n_rows)]
    # col_signs[j] is -1 when column j is flipped and 1 otherwise
    col_signs = [model.intvar([-1, 1], name=f"col_sign_{j}") for j in range(n_cols)]

    # cell_sign[i][j] is the sign applied to the number in row i and column j
    cell_sign = [[model.intvar([-1, 1], name=f"cell_sign_{i}_{j}") for j in range(n_cols)]
                 for i in range(n_rows)]
    # A number is flipped by its row and by its column, so its sign is the product of the two signs.
    for i in range(n_rows):
        for j in range(n_cols):
            model.times(row_signs[i], col_signs[j], cell_sign[i][j]).post()

    # Every row and every column of the flipped array sums to zero or more.
    # Such a sum is at most the sum of the absolute values of its numbers.
    for i in range(n_rows):
        row_sum = model.intvar(0, sum(abs(v) for v in matrix[i]), name=f"row_sum_{i}")
        model.scalar(cell_sign[i], matrix[i], "=", row_sum).post()
    for j in range(n_cols):
        column = [matrix[i][j] for i in range(n_rows)]
        col_sum = model.intvar(0, sum(abs(v) for v in column), name=f"col_sum_{j}")
        model.scalar([cell_sign[i][j] for i in range(n_rows)], column, "=", col_sum).post()

    # The overall sum of the flipped array, which is to be as small as possible.
    total_sum = model.intvar(0, sum(abs(v) for row in matrix for v in row), name="total_sum")
    model.scalar(
        [cell_sign[i][j] for i in range(n_rows) for j in range(n_cols)],
        [matrix[i][j] for i in range(n_rows) for j in range(n_cols)],
        "=",
        total_sum,
    ).post()

    return model, {"row_signs": row_signs, "col_signs": col_signs}, {"objective": total_sum, "maximize": False}


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
