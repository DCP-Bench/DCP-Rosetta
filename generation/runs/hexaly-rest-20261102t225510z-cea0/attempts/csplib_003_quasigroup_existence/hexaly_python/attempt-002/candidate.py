"""Quasigroup existence QG3.m: an order m Latin square in which (a * b) * (b * a) = a for all a, b."""
import hexaly.optimizer as hx


def build(instance):
    m = instance["m"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # has[a][b][v] = 1 if the product a * b is v. Booleans with linear constraints give Hexaly
    # bounds that integer cells compared through an element lookup do not.
    has = [[[model.bool() for _ in range(m)] for _ in range(m)] for _ in range(m)]

    # Every product is one element
    for a in range(m):
        for b in range(m):
            model.constraint(model.sum(has[a][b]) == 1)
    # A Latin square: each element occurs once in every row and every column
    for v in range(m):
        for a in range(m):
            model.constraint(model.sum(has[a][b][v] for b in range(m)) == 1)
            model.constraint(model.sum(has[b][a][v] for b in range(m)) == 1)

    # The QG3 property: if a * b = c and b * a = d, then c * d = a
    for a in range(m):
        for b in range(m):
            for c in range(m):
                for d in range(m):
                    model.constraint(has[a][b][c] + has[b][a][d] - 1 <= has[c][d][a])

    quasigroup = [[model.sum(v * has[a][b][v] for v in range(m)) for b in range(m)] for a in range(m)]
    return optimizer, {"quasigroup": quasigroup}
