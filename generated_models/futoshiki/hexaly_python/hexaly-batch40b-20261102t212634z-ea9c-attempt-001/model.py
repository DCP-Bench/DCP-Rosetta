"""Futoshiki: a Latin square with some given digits and inequalities between some squares."""
import hexaly.optimizer as hx


def build(instance):
    values, lt = instance["values"], instance["lt"]  # lt rows (r1, c1, r2, c2), 1-based: square 1 < square 2
    n = len(values)
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # has[r][c][v] = 1 if square (r, c) holds v + 1; Booleans with linear sums
    has = [[[model.bool() for _ in range(n)] for _ in range(n)] for _ in range(n)]
    for r in range(n):
        for c in range(n):
            model.constraint(model.sum(has[r][c]) == 1)
    # Every row and every column holds each digit once
    for v in range(n):
        for r in range(n):
            model.constraint(model.sum(has[r][c][v] for c in range(n)) == 1)
        for c in range(n):
            model.constraint(model.sum(has[r][c][v] for r in range(n)) == 1)
    grid = [[model.sum((v + 1) * has[r][c][v] for v in range(n)) for c in range(n)] for r in range(n)]

    # The given digits (non-zero entries) stay
    for r in range(n):
        for c in range(n):
            if values[r][c]:
                model.constraint(grid[r][c] == values[r][c])
    # The inequalities between squares
    for r1, c1, r2, c2 in lt:
        model.constraint(grid[r1 - 1][c1 - 1] < grid[r2 - 1][c2 - 1])

    return optimizer, {"grid": grid}
