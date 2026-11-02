"""Magic square: an n x n grid of the distinct integers 1..n^2 whose rows, columns and diagonals sum to the same value."""
import hexaly.optimizer as hx


def build(instance):
    n = instance["n"]
    magic = n * (n * n + 1) // 2  # the common sum the problem statement fixes
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # The cells hold 1..n^2, each once: a full list decision read row by row
    perm = model.list(n * n)
    model.constraint(model.count(perm) == n * n)
    square = [[perm[i * n + j] + 1 for j in range(n)] for i in range(n)]

    # Every row and every column sums to the magic constant
    for i in range(n):
        model.constraint(model.sum(square[i]) == magic)
        model.constraint(model.sum(square[r][i] for r in range(n)) == magic)
    # So do both diagonals
    model.constraint(model.sum(square[i][i] for i in range(n)) == magic)
    model.constraint(model.sum(square[i][n - 1 - i] for i in range(n)) == magic)

    return optimizer, {"square": square}
