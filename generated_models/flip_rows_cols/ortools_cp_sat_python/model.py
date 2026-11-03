# flip_rows_cols: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `flip_rows_cols.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/flip_rows_cols.html
# Then run it on the first instance (after `pip install ortools`):
#   python flip_rows_cols.py flip_rows_cols.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Flip the signs of any rows and columns of an array of positive and negative
    numbers, so that every row and every column sums to a positive number or zero,
    with the smallest overall sum. Print the sign of each row and each column, as -1 or 1."""
    matrix = instance["input_matrix"]  # matrix[i][j]: the number in row i, column j
    n_rows = len(matrix)               # the number of rows
    n_cols = len(matrix[0])            # the number of columns

    model = cp_model.CpModel()

    # row_flipped[i] is true when row i is flipped; col_flipped[j] is true when column j is flipped
    row_flipped = [model.new_bool_var(f"row_flipped_{i}") for i in range(n_rows)]
    col_flipped = [model.new_bool_var(f"col_flipped_{j}") for j in range(n_cols)]
    # row_signs[i] is the sign of row i and col_signs[j] the sign of column j
    row_signs = [model.new_int_var_from_domain(cp_model.Domain.from_values([-1, 1]), f"row_sign_{i}") for i in range(n_rows)]
    col_signs = [model.new_int_var_from_domain(cp_model.Domain.from_values([-1, 1]), f"col_sign_{j}") for j in range(n_cols)]
    # A flipped row or column has sign -1, the others sign 1.
    for i in range(n_rows):
        model.add(row_signs[i] == 1 - 2 * row_flipped[i])
    for j in range(n_cols):
        model.add(col_signs[j] == 1 - 2 * col_flipped[j])

    # x[i][j] is the entry in row i and column j after the flips, within -100..100
    x = [[None] * n_cols for _ in range(n_rows)]
    for i in range(n_rows):
        for j in range(n_cols):
            # cell_flipped is true when row i or column j is flipped, but not both
            cell_flipped = model.new_bool_var(f"cell_flipped_{i}_{j}")
            model.add_bool_xor([row_flipped[i], col_flipped[j], ~cell_flipped])
            x[i][j] = model.new_int_var(-100, 100, f"x_{i}_{j}")
            # The entry keeps its size and changes sign when the cell is flipped.
            model.add(x[i][j] == matrix[i][j] * (1 - 2 * cell_flipped))

    # Every row and every column sums to between 0 and 300.
    for i in range(n_rows):
        model.add(sum(x[i]) >= 0)
        model.add(sum(x[i]) <= 300)
    for j in range(n_cols):
        model.add(sum(x[i][j] for i in range(n_rows)) >= 0)
        model.add(sum(x[i][j] for i in range(n_rows)) <= 300)

    # The overall sum of the flipped array.
    total_sum = model.new_int_var(0, 1000, "total_sum")
    # total_sum adds up every entry.
    model.add(total_sum == sum(sum(row) for row in x))

    # Minimize the overall sum.
    model.minimize(total_sum)

    return model, {"row_signs": row_signs, "col_signs": col_signs}


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
