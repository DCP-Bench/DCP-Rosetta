"""Bus scheduling: buses start in 4-hour slots and run 8 hours; cover each slot's demand with the fewest buses."""
import hexaly.optimizer as hx


def build(instance):
    demands = instance["demands"]
    n = len(demands)
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # x[i] is the number of buses that start in slot i. An optimum never starts more than the
    # largest demand in one slot, since fewer would still cover both slots that bus serves.
    x = [model.int(0, max(demands)) for _ in range(n)]

    # A bus runs two successive slots, the day wrapping around: slot i + 1 is served by the
    # buses that started in slot i and those starting in slot i + 1
    for i in range(n):
        model.constraint(x[i] + x[(i + 1) % n] >= demands[(i + 1) % n])

    # Minimise the number of buses
    model.minimize(model.sum(x))
    return optimizer, {"x": x}
