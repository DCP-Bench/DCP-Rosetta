"""Quasigroup existence QG3.m: an order m Latin square in which (a * b) * (b * a) = a for all a, b."""
import hexaly.optimizer as hx


def build(instance):
    m = instance["m"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # quasigroup[a][b] is the product a * b, an element 0..m-1
    quasigroup = [[model.int(0, m - 1) for _ in range(m)] for _ in range(m)]

    # A Latin square: each element occurs once in every row and every column
    for r in range(m):
        for a in range(m):
            for b in range(a + 1, m):
                model.constraint(quasigroup[r][a] != quasigroup[r][b])
                model.constraint(quasigroup[a][r] != quasigroup[b][r])

    # The QG3 property: (a * b) * (b * a) = a, reading the product of two results from the table itself
    table = model.array(quasigroup)
    for a in range(m):
        for b in range(m):
            model.constraint(model.at(table, quasigroup[a][b], quasigroup[b][a]) == a)

    return optimizer, {"quasigroup": quasigroup}
