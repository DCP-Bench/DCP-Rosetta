"""Bowls and oranges: put m oranges in n bowls in a line, at most one per bowl, with no three equally spaced."""
import hexaly.optimizer as hx


def build(instance):
    n, m = instance["n"], instance["m"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # x[k] is the bowl (numbered 1..n) of the k-th orange, in ascending order;
    # strictly ascending also keeps it to one orange per bowl
    x = [model.int(1, n) for _ in range(m)]
    for k in range(m - 1):
        model.constraint(x[k] < x[k + 1])

    # No three oranges A < B < C with B as far from A as C is from B
    for a in range(m):
        for b in range(a + 1, m):
            for c in range(b + 1, m):
                model.constraint(x[b] - x[a] != x[c] - x[b])

    return optimizer, {"x": x}
