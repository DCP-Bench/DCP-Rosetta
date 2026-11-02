"""All-interval series: a permutation of 0..n-1 whose neighbouring intervals are a permutation of 1..n-1."""
import hexaly.optimizer as hx


def build(instance):
    n = instance["n"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # x is a permutation of 0..n-1: a list decision holding every value once
    x = model.list(n)
    model.constraint(model.count(x) == n)

    # The interval between neighbouring notes; with distinct notes it lies in 1..n-1
    diffs = [model.abs(x[i + 1] - x[i]) for i in range(n - 1)]
    # The n - 1 intervals are all different, so they cover 1..n-1
    model.constraint(model.count(model.distinct(model.array(diffs))) == n - 1)

    return optimizer, {"x": x, "diffs": diffs}
