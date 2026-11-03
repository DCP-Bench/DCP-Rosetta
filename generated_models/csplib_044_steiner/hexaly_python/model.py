"""Ternary Steiner system: n(n-1)/6 triples of the elements 1..n, any two sharing at most one element."""
import hexaly.optimizer as hx


def build(instance):
    n = instance["n"]  # order of the system: the elements are 1..n (n mod 6 is 1 or 3)
    triples = n * (n - 1) // 6  # the number of triples, n * (n - 1) / 6, as the problem statement fixes it
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # sets[i][j] = 1 if element j + 1 is part of triple i (rows are triples, columns are elements)
    sets = [[model.bool() for _ in range(n)] for _ in range(triples)]

    # Every triple consists of exactly three distinct elements of 1..n
    for i in range(triples):
        model.constraint(model.sum(sets[i]) == 3)
    # Any two triples have at most one common element (which also keeps the triples distinct,
    # since two equal triples would share three)
    for i in range(triples):
        for k in range(i + 1, triples):
            model.constraint(model.sum(sets[i][j] * sets[k][j] for j in range(n)) <= 1)

    return optimizer, {"sets": sets}
