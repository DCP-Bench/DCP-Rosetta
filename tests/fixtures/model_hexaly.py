import hexaly.optimizer as hx


def build(instance):
    n = instance["n"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model
    x = model.int(0, n)
    y = model.int(0, n)
    if instance["optimize"]:
        model.constraint(x + y >= n)
        model.minimize(x + y)
    else:
        model.constraint(x + y == n)
    return optimizer, {"x": x, "y": y}
