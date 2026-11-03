"""Discrete tomography: a 0/1 matrix with the given number of ones in each row and each column."""
import hexaly.optimizer as hx


def build(instance):
    row_sums, col_sums = instance["row_sums"], instance["col_sums"]
    rows, cols = len(row_sums), len(col_sums)
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    matrix = [[model.bool() for _ in range(cols)] for _ in range(rows)]

    # Each row and each column has its given number of ones
    for i in range(rows):
        model.constraint(model.sum(matrix[i]) == row_sums[i])
    for j in range(cols):
        model.constraint(model.sum(matrix[i][j] for i in range(rows)) == col_sums[j])

    return optimizer, {"matrix": matrix}
