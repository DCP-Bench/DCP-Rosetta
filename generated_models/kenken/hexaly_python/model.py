"""KenKen: a Latin square whose cages reach their result by some operation (+, -, x or /), the operations unstated."""
from itertools import product
from math import prod

import hexaly.optimizer as hx


def reaches(values, result):
    """Whether the cage digits reach the result: by addition or multiplication, and for two cells
    also by subtraction or division in either order."""
    if sum(values) == result or prod(values) == result:
        return True
    if len(values) == 2:
        a, b = values
        return abs(a - b) == result or a == result * b or b == result * a
    return False


def build(instance):
    n, cages = instance["n"], instance["problem"]  # cages: [result, [[row, col], ...]] with 1-based cells
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # x[r][c] is the digit (1..n) in cell (r, c)
    x = [[model.int(1, n) for _ in range(n)] for _ in range(n)]
    # Every row and every column holds each digit once
    for r in range(n):
        for a in range(n):
            for b in range(a + 1, n):
                model.constraint(x[r][a] != x[r][b])
                model.constraint(x[a][r] != x[b][r])

    # Each cage takes one of the digit combinations that reach its result, listed from the data:
    # a table constraint the search can move between directly
    for result, cells in cages:
        cell_vars = [x[r - 1][c - 1] for r, c in cells]
        allowed = [t for t in product(range(1, n + 1), repeat=len(cells)) if reaches(t, result)]
        model.constraint(model.or_(*[model.and_(*[v == d for v, d in zip(cell_vars, t)]) for t in allowed]))

    return optimizer, {"x": x}
