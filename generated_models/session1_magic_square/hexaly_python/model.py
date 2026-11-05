"""Magic square: an n x n grid of the distinct integers 1..n^2 whose rows, columns and diagonals sum to the same value."""
import hexaly.optimizer as hx


def build(instance):
    n = instance["n"]  # side of the magic square: n x n cells (n is not 2)
    magic = n * (n * n + 1) // 2  # n(n^2 + 1)/2, the sum of each row, column and diagonal as the problem statement fixes it
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # perm[i * n + j] = (integer in row i, column j) - 1, the grid read row by row; a list decision of size n * n
    perm = model.list(n * n)
    # Each cell contains a different integer from 1 to n^2: the list must use all n * n values, so perm is a permutation of 0..n^2-1
    model.constraint(model.count(perm) == n * n)
    # square[i][j] = the integer in row i, column j (1..n^2), the permutation shifted up by one
    square = [[perm[i * n + j] + 1 for j in range(n)] for i in range(n)]

    # The integers in each row and in each column sum to the magic constant
    for i in range(n):
        model.constraint(model.sum(square[i]) == magic)
        model.constraint(model.sum(square[r][i] for r in range(n)) == magic)
    # The integers in both diagonals also sum to the magic constant
    model.constraint(model.sum(square[i][i] for i in range(n)) == magic)
    model.constraint(model.sum(square[i][n - 1 - i] for i in range(n)) == magic)

    return optimizer, {"square": square}
