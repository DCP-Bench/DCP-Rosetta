"""Coins: the fewest coins of the given denominations that pay exactly every amount below the maximum."""
import hexaly.optimizer as hx


def build(instance):
    denominations, top = instance["denominations"], instance["max_amount_to_pay"]
    k = len(denominations)
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # x[i] is the number of coins of denomination i; paying amounts below top never needs more
    # than top // denomination of one kind
    x = [model.int(0, top // d) for d in denominations]

    # Every amount from 1 to top - 1 is paid exactly with some of the coins held
    for amount in range(1, top):
        pay = [model.int(0, top // d) for d in denominations]
        for i in range(k):
            model.constraint(pay[i] <= x[i])
        model.constraint(model.sum(denominations[i] * pay[i] for i in range(k)) == amount)

    # Minimise the number of coins
    model.minimize(model.sum(x))
    return optimizer, {"x": x}
