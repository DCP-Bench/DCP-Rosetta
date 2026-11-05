"""Heterosquare: an n x n square of the distinct integers 1..n^2 whose row, column and diagonal sums all differ."""
import hexaly.optimizer as hx


def build(instance):
    n = instance["n"]  # n = the order of the square: n rows and n columns, filled with 1..n^2
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # perm = the entries of the square read row by row: perm[i * n + j] + 1 is the entry in row i, column j.
    # A list decision holds each value of 0..n^2-1 at most once, so the entries are distinct;
    # a list may be shorter than n^2, which the next constraint rules out
    perm = model.list(n * n)
    # The elements are the integers from 1 to n^2: the list has all n^2 values, i.e. is a permutation
    model.constraint(model.count(perm) == n * n)
    # x[i][j] = the integer in row i, column j of the square (1..n^2)
    x = [[perm[i * n + j] + 1 for j in range(n)] for i in range(n)]

    # The sums of the rows, the columns and the two diagonals are all different:
    # sums holds the n row sums, the n column sums, the main diagonal and the anti-diagonal
    sums = [model.sum(x[i]) for i in range(n)] + [model.sum(x[i][j] for i in range(n)) for j in range(n)]
    sums.append(model.sum(x[i][i] for i in range(n)))
    sums.append(model.sum(x[i][n - 1 - i] for i in range(n)))
    for a in range(len(sums)):
        for b in range(a + 1, len(sums)):
            model.constraint(sums[a] != sums[b])

    return optimizer, {"x": x}
