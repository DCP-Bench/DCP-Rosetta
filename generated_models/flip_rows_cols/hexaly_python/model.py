"""Flip rows and columns: choose signs for rows and columns so every row and column sums to at least 0,
with the smallest overall sum."""
import hexaly.optimizer as hx


def build(instance):
    a = instance["input_matrix"]  # a[i][j] = the positive or negative number in row i, column j of the array
    rows, cols = len(a), len(a[0])  # number of rows and columns of the array
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # row_signs[i] = -1 if the sign of row i is flipped, +1 if it is kept; the 0/1 bit is mapped to a sign as 2 * bit - 1
    row_signs = [2 * model.bool() - 1 for _ in range(rows)]
    # col_signs[j] = -1 if the sign of column j is flipped, +1 if it is kept
    col_signs = [2 * model.bool() - 1 for _ in range(cols)]
    # flipped[i][j] = the array after flipping; a cell changes sign if exactly one of its row and its column is flipped
    flipped = [[a[i][j] * row_signs[i] * col_signs[j] for j in range(cols)] for i in range(rows)]

    # Each one of all the rows and columns must sum to a positive number (or zero): first the rows
    for i in range(rows):
        model.constraint(model.sum(flipped[i]) >= 0)
    # ... then the columns
    for j in range(cols):
        model.constraint(model.sum(flipped[i][j] for i in range(rows)) >= 0)

    # Minimise the overall sum of the flipped array, among the solutions where every row and column sums to at least 0
    model.minimize(model.sum(flipped[i][j] for i in range(rows) for j in range(cols)))
    return optimizer, {"row_signs": row_signs, "col_signs": col_signs}
