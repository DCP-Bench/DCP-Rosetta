# flip_rows_cols: an Exact (Python) model from DCP Rosetta.
# Download the `flip_rows_cols.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/flip_rows_cols.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python flip_rows_cols.py flip_rows_cols.json

from exact import Exact


def create_model(instance):
    """Flip the signs of whole rows and columns of a matrix of positive and negative numbers, so
    that every row and every column sums to zero or more, choosing the flips with the smallest
    total."""
    matrix = instance["input_matrix"]  # matrix[i][j]: the number in row i, column j
    n_rows, n_cols = len(matrix), len(matrix[0])  # the size of the matrix

    solver = Exact()

    # Exact identifies its variables by name.
    # row_flipped[i] is 1 when row i is flipped, and 0 when not
    row_flipped = [f"row_flipped_{i}" for i in range(n_rows)]
    # col_flipped[j] is 1 when column j is flipped, and 0 when not
    col_flipped = [f"col_flipped_{j}" for j in range(n_cols)]
    for name in row_flipped + col_flipped:
        solver.addVariable(name, 0, 1)

    # row_signs[i] and col_signs[j] are the signs chosen for row i and column j
    row_signs = [f"row_sign_{i}" for i in range(n_rows)]
    col_signs = [f"col_sign_{j}" for j in range(n_cols)]
    for name in row_signs + col_signs:
        solver.addVariable(name, -1, 1)

    # cell_flipped[i][j] is 1 when cell (i, j) is flipped, and 0 when not
    cell_flipped = [[f"cell_flipped_{i}_{j}" for j in range(n_cols)] for i in range(n_rows)]
    for i in range(n_rows):
        for j in range(n_cols):
            solver.addVariable(cell_flipped[i][j], 0, 1)

    # The change in a sum when the given cells are flipped: each flipped cell with entry x adds -2x.
    def flipped_terms(cells):
        return [(-2 * matrix[i][j], cell_flipped[i][j]) for i, j in cells if matrix[i][j] != 0]

    # A row has sign -1 when it is flipped, and 1 when not. The same holds for columns.
    for i in range(n_rows):
        solver.addConstraint([(1, row_signs[i]), (2, row_flipped[i])], True, 1, True, 1)
    for j in range(n_cols):
        solver.addConstraint([(1, col_signs[j]), (2, col_flipped[j])], True, 1, True, 1)

    # A cell is flipped exactly when one of its row and its column is flipped, not both.
    for i in range(n_rows):
        for j in range(n_cols):
            cell, row, col = cell_flipped[i][j], row_flipped[i], col_flipped[j]
            solver.addConstraint([(1, cell), (-1, row), (-1, col)], False, 0, True, 0)
            solver.addConstraint([(1, cell), (1, row), (1, col)], False, 0, True, 2)
            solver.addConstraint([(1, cell), (1, row), (-1, col)], True, 0)
            solver.addConstraint([(1, cell), (-1, row), (1, col)], True, 0)

    # Each row sums to between 0 and 300 after flipping.
    for i in range(n_rows):
        row_cells = [(i, j) for j in range(n_cols)]  # the cells of row i
        row_total = sum(matrix[i][j] for j in range(n_cols))  # the sum of row i before flipping
        solver.addConstraint(flipped_terms(row_cells), True, -row_total, True, 300 - row_total)

    # Each column sums to between 0 and 300 after flipping.
    for j in range(n_cols):
        col_cells = [(i, j) for i in range(n_rows)]  # the cells of column j
        col_total = sum(matrix[i][j] for i in range(n_rows))  # the sum of column j before flipping
        solver.addConstraint(flipped_terms(col_cells), True, -col_total, True, 300 - col_total)

    # The total of the matrix after flipping lies between 0 and 1000.
    all_cells = [(i, j) for i in range(n_rows) for j in range(n_cols)]  # every cell of the matrix
    grand_total = sum(matrix[i][j] for i, j in all_cells)  # the total before flipping
    solver.addConstraint(flipped_terms(all_cells), True, -grand_total, True, 1000 - grand_total)

    # The smallest total of the matrix after flipping.
    solver.setObjective(flipped_terms(all_cells), minimize=True)

    return solver, {"row_signs": row_signs, "col_signs": col_signs}


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
