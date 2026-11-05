"""Quasigroup completion: complete a partially filled N x N Latin square (each of 1..N once per row and column).

The given cells keep their values and every empty cell is filled so that each value
from 1 to N occurs exactly once in every row and every column.
"""
import hexaly.optimizer as hx


def build(instance):
    # N: side of the square and number of distinct values
    # start[i][j]: the value (1..N) given in cell (i, j), 0 if the cell is empty
    n, start = instance["N"], instance["start"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # has[i][j][v] = 1 if cell (i, j) holds the value v + 1. Booleans with linear sums keep the
    # model linear, the form Hexaly proves bounds on.
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
    # (the one true has[i][j][v] gives the value v + 1 of cell (i, j))
    puzzle = [[model.sum((v + 1) * has[i][j][v] for v in range(n)) for j in range(n)] for i in range(n)]
    return optimizer, {"puzzle": puzzle}
