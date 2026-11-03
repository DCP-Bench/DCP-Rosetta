"""Heterosquare: an n x n square of the distinct integers 1..n^2 whose row, column and diagonal sums all differ."""
import hexaly.optimizer as hx


def build(instance):
    n = instance["n"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # The entries are 1..n^2, each once: a full list decision read row by row
    perm = model.list(n * n)
    model.constraint(model.count(perm) == n * n)
    x = [[perm[i * n + j] + 1 for j in range(n)] for i in range(n)]

    # The sums of the rows, the columns and the two diagonals are all different
    sums = [model.sum(x[i]) for i in range(n)] + [model.sum(x[i][j] for i in range(n)) for j in range(n)]
    sums.append(model.sum(x[i][i] for i in range(n)))
    sums.append(model.sum(x[i][n - 1 - i] for i in range(n)))
    for a in range(len(sums)):
        for b in range(a + 1, len(sums)):
            model.constraint(sums[a] != sums[b])

    return optimizer, {"x": x}
