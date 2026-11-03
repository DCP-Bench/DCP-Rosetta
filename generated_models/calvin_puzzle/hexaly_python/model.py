"""Calvin puzzle: number the squares of an n x n grid 1..n^2 so that each number is three squares from the
previous one horizontally or vertically, or two squares away diagonally."""
import hexaly.optimizer as hx


def build(instance):
    n = instance["n"]  # the grid has n rows and n columns
    cells = n * n
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # path[t] is the square (row * n + col) holding the number t + 1: every square once
    path = model.list(cells)
    model.constraint(model.count(path) == cells)

    for t in range(cells - 1):
        dr = model.abs(path[t] // n - path[t + 1] // n)
        dc = model.abs(path[t] % n - path[t + 1] % n)
        # Straight: exactly three squares away along a row or column (a gap of two); diagonal:
        # exactly two squares away along both (a gap of one)
        model.constraint(model.or_(model.and_(dr == 3, dc == 0), model.and_(dr == 0, dc == 3),
                                   model.and_(dr == 2, dc == 2)))

    # The number written in each square
    x = [[model.index(path, r * n + c) + 1 for c in range(n)] for r in range(n)]
    return optimizer, {"x": x}
