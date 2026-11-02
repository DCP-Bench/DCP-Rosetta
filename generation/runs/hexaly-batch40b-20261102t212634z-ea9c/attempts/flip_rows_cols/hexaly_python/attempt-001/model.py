"""Flip rows and columns: choose signs for rows and columns so every row and column sums to at least 0,
with the smallest overall sum."""
import hexaly.optimizer as hx


def build(instance):
    a = instance["input_matrix"]
    rows, cols = len(a), len(a[0])
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # row_signs[i], col_signs[j] in {-1, +1}, written as 2 * bit - 1
    row_signs = [2 * model.bool() - 1 for _ in range(rows)]
    col_signs = [2 * model.bool() - 1 for _ in range(cols)]
    # The matrix after flipping
    flipped = [[a[i][j] * row_signs[i] * col_signs[j] for j in range(cols)] for i in range(rows)]

    # Every row and every column sums to a non-negative number
    for i in range(rows):
        model.constraint(model.sum(flipped[i]) >= 0)
    for j in range(cols):
        model.constraint(model.sum(flipped[i][j] for i in range(rows)) >= 0)

    # Minimise the overall sum
    model.minimize(model.sum(flipped[i][j] for i in range(rows) for j in range(cols)))
    return optimizer, {"row_signs": row_signs, "col_signs": col_signs}
