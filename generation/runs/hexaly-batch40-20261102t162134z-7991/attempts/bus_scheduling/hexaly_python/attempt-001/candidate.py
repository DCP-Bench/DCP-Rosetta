"""Bus scheduling: buses start in 4-hour slots and run 8 hours; cover each slot's demand with the fewest buses."""
import hexaly.optimizer as hx


def build(instance):
    demands = instance["demands"]
    n = len(demands)
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # x[i] is the number of buses that start in slot i; no slot needs more than the largest demand
    x = [model.int(0, max(demands)) for _ in range(n)]

    # A bus runs two successive slots, the day wrapping around: the buses starting in slot i
    # and in slot i + 1 together meet the demand of slot i
    for i in range(n):
        model.constraint(x[i] + x[(i + 1) % n] >= demands[i])

    # Minimise the number of buses
    model.minimize(model.sum(x))
    return optimizer, {"x": x}
