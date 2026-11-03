"""Among: an array x of n values in 0..7 in which exactly m entries take one of the values in v."""
import hexaly.optimizer as hx


def build(instance):
    n, m, v = instance["n"], instance["m"], instance["v"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # Every entry lies between 0 and 7, as the problem statement fixes
    x = [model.int(0, 7) for _ in range(n)]

    # Exactly m entries take a value from v
    in_v = [model.or_(*[x[i] == value for value in v]) if v else 0 for i in range(n)]
    model.constraint(model.sum(in_v) == m)

    return optimizer, {"x": x}
