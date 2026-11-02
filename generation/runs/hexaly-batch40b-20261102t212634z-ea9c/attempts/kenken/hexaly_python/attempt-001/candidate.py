"""KenKen: a Latin square whose cages reach their result by some operation (+, -, x or /), the operations unstated."""
import hexaly.optimizer as hx


def build(instance):
    n, cages = instance["n"], instance["problem"]  # cages: [result, [[row, col], ...]] with 1-based cells
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # has[r][c][v] = 1 if cell (r, c) holds v + 1; every row and column holds each digit once
    has = [[[model.bool() for _ in range(n)] for _ in range(n)] for _ in range(n)]
    for r in range(n):
        for c in range(n):
            model.constraint(model.sum(has[r][c]) == 1)
    for v in range(n):
        for r in range(n):
            model.constraint(model.sum(has[r][c][v] for c in range(n)) == 1)
        for c in range(n):
            model.constraint(model.sum(has[r][c][v] for r in range(n)) == 1)
    x = [[model.sum((v + 1) * has[r][c][v] for v in range(n)) for c in range(n)] for r in range(n)]

    for result, cells in cages:
        values = [x[r - 1][c - 1] for r, c in cells]
        if len(values) == 2:
            a, b = values
            # Two cells: their sum, product, difference or quotient (in either order) is the result
            model.constraint(model.or_(a + b == result, a * b == result, a - b == result, b - a == result,
                                       a == result * b, b == result * a))
        else:
            # One cell holds the result; a larger cage reaches it by addition or multiplication
            model.constraint(model.or_(model.sum(values) == result, model.prod(values) == result))

    return optimizer, {"x": x}
