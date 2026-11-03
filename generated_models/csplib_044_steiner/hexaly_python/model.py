"""Ternary Steiner system: n(n-1)/6 triples of the elements 1..n, any two sharing at most one element."""
import hexaly.optimizer as hx


def build(instance):
    n = instance["n"]
    triples = n * (n - 1) // 6
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # sets[i][j] = 1 if element j is in triple i
    sets = [[model.bool() for _ in range(n)] for _ in range(triples)]

    # Every triple has exactly three distinct elements
    for i in range(triples):
        model.constraint(model.sum(sets[i]) == 3)
    # Any two triples have at most one common element (which also keeps the triples distinct)
    for i in range(triples):
        for k in range(i + 1, triples):
            model.constraint(model.sum(sets[i][j] * sets[k][j] for j in range(n)) <= 1)

    return optimizer, {"sets": sets}
