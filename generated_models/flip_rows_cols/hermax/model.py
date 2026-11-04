# flip_rows_cols: a hermax (Python) model from DCP Rosetta.
# Download the `flip_rows_cols.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/flip_rows_cols.html
# Then run it on the first instance (after `pip install hermax`):
#   python flip_rows_cols.py flip_rows_cols.json

from hermax.model import Model, sum_expr


def create_model(instance):
    """Choose which rows and which columns of a matrix to flip in sign, so that every row and
    every column sums to a non-negative number, with the smallest possible total of all entries."""
    # input_matrix: the given matrix, a list of rows of integers
    matrix = instance["input_matrix"]
    # rows, cols: number of rows and columns of the matrix
    rows = len(matrix)
    cols = len(matrix[0])

    m = Model()

    # row_flip[i] is true when row i is flipped in sign
    row_flip = [m.bool(f"row_flip_{i}") for i in range(rows)]
    # col_flip[j] is true when column j is flipped in sign
    col_flip = [m.bool(f"col_flip_{j}") for j in range(cols)]
    # cell_flip[i][j] is true when entry (i, j) changes sign, that is when exactly one of its row
    # and its column is flipped
    cell_flip = [[m.bool(f"cell_flip_{i}_{j}") for j in range(cols)] for i in range(rows)]

    # Each cell_flip is true exactly when one of its row_flip and col_flip is true.
    for i in range(rows):
        for j in range(cols):
            m &= (row_flip[i] + col_flip[j] == 1).iff(cell_flip[i][j])

    # signed(i, j) is entry (i, j) after the flips: its value when not flipped, its negation when
    # flipped, written as a linear expression over the cell's Boolean.
    def signed(i, j):
        a = matrix[i][j]
        return a - 2 * a * cell_flip[i][j]

    # Every row sums to a non-negative number after the flips.
    for i in range(rows):
        m &= (sum_expr(signed(i, j) for j in range(cols)) >= 0)

    # Every column sums to a non-negative number after the flips.
    for j in range(cols):
        m &= (sum_expr(signed(i, j) for i in range(rows)) >= 0)

    # total is the sum of all entries after the flips. It lies between minus and plus the sum of
    # the absolute values of all entries, and is tied to the cost expression so that the objective
    # is one bounded integer.
    mass = sum(abs(matrix[i][j]) for i in range(rows) for j in range(cols))
    total = m.int("total", -mass, mass)
    m &= (total == sum_expr(signed(i, j) for i in range(rows) for j in range(cols)))

    # Minimise the total of all entries after the flips.
    m.obj += total

    return m, {
        # the sign of a row or column: 1 when not flipped, -1 when flipped
        "row_signs": [1 - 2 * row_flip[i] for i in range(rows)],
        "col_signs": [1 - 2 * col_flip[j] for j in range(cols)],
    }


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
