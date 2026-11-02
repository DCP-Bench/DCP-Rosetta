"""Broken weights: n whole-pound pieces of total m that weigh every integer 1..m on a balance scale."""
import hexaly.optimizer as hx


def build(instance):
    m, n = instance["m"], instance["n"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # weights[i] is the weight of piece i, listed in ascending order (the pieces are interchangeable)
    weights = [model.int(1, m) for _ in range(n)]
    for i in range(n - 1):
        model.constraint(weights[i] <= weights[i + 1])
    # The pieces make up the whole weight
    model.constraint(model.sum(weights) == m)

    # Implied, to guide the search: sorted pieces weigh every integer up to their total exactly
    # when each piece is at most twice the total of the lighter ones plus 1. Checked by brute
    # force against the definition for every split of m <= 80 into at most 5 pieces.
    for i in range(n):
        model.constraint(weights[i] <= 2 * model.sum(weights[:i]) + 1)

    # Every weight w from 1 to m can be weighed: side[i] puts piece i on the object's side (-1),
    # off the scale (0) or on the other side (1)
    for w in range(1, m + 1):
        side = [model.int(-1, 1) for _ in range(n)]
        model.constraint(model.sum(side[i] * weights[i] for i in range(n)) == w)

    return optimizer, {"weights": weights}
