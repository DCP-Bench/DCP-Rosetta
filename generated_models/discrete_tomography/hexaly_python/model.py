"""Discrete tomography: a 0/1 matrix with the given number of ones in each row and each column."""
import hexaly.optimizer as hx


def build(instance):
    # row_sums[i] = number of ones in row i, col_sums[j] = number of ones in column j, as given by the x-ray
    row_sums, col_sums = instance["row_sums"], instance["col_sums"]
    rows, cols = len(row_sums), len(col_sums)  # dimensions of the matrix to reconstruct
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # matrix[i][j] = 1 if the cell in row i and column j holds a one, 0 if it holds a zero
    matrix = [[model.bool() for _ in range(cols)] for _ in range(rows)]

    # The total number of ones in each row and in each column matches the x-ray: first the rows
    for i in range(rows):
        model.constraint(model.sum(matrix[i]) == row_sums[i])
    # ... then the columns
    for j in range(cols):
        model.constraint(model.sum(matrix[i][j] for i in range(rows)) == col_sums[j])

    return optimizer, {"matrix": matrix}
