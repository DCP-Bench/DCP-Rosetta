"""Bowls and oranges: put m oranges in n bowls placed in a line 1 meter apart, at most one orange per bowl, so that
no three oranges A, B, C have the distance from A to B equal to the distance from B to C."""
import hexaly.optimizer as hx


def build(instance):
    n, m = instance["n"], instance["m"]  # n = number of bowls in the line, m = number of oranges to place
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # x[k] = number of the bowl (1..n, bowls are 1 meter apart) holding the k-th orange, in ascending order
    x = [model.int(1, n) for _ in range(m)]
    # Bowls are listed in ascending order; strictly ascending also keeps it to at most one orange per bowl
    for k in range(m - 1):
        model.constraint(x[k] < x[k + 1])

    # No three oranges A < B < C with B as far from A as C is from B. Since x is ascending, taking the
    # oranges in index order a < b < c makes B the middle one, so the two distances are x[b] - x[a] and x[c] - x[b].
    for a in range(m):
        for b in range(a + 1, m):
            for c in range(b + 1, m):
                model.constraint(x[b] - x[a] != x[c] - x[b])

    return optimizer, {"x": x}
