"""Quasigroup completion: complete a partially filled N x N Latin square (each of 1..N once per row and column)."""
import hexaly.optimizer as hx


def build(instance):
    n, start = instance["N"], instance["start"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # has[i][j][v] = 1 if cell (i, j) holds the value v + 1. Booleans with linear sums give
    # Hexaly bounds it can use, where integers with all-different would not.
    has = [[[model.bool() for _ in range(n)] for _ in range(n)] for _ in range(n)]

    # Every cell holds exactly one value
    for i in range(n):
        for j in range(n):
            model.constraint(model.sum(has[i][j]) == 1)
    # Every value occurs exactly once in each row and once in each column
    for v in range(n):
        for i in range(n):
            model.constraint(model.sum(has[i][j][v] for j in range(n)) == 1)
        for j in range(n):
            model.constraint(model.sum(has[i][j][v] for i in range(n)) == 1)
    # The given cells (non-zero in start) keep their values
    for i in range(n):
        for j in range(n):
            if start[i][j]:
                model.constraint(has[i][j][start[i][j] - 1] == 1)

    # The completed square, as the value 1..N of each cell
    puzzle = [[model.sum((v + 1) * has[i][j][v] for v in range(n)) for j in range(n)] for i in range(n)]
    return optimizer, {"puzzle": puzzle}
