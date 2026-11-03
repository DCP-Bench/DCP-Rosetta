"""Coins: the fewest coins of the given denominations that pay exactly every amount below the maximum."""
import hexaly.optimizer as hx


def build(instance):
    # denominations[i] = value of coin type i; max_amount_to_pay = the amounts to pay are all those below it
    denominations, top = instance["denominations"], instance["max_amount_to_pay"]
    k = len(denominations)  # number of coin types
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # x[i] = number of coins of denomination i that are held.
    # Upper bound (derived): paying an amount below top never uses more than top // denomination
    # coins of one kind.
    x = [model.int(0, top // d) for d in denominations]

    # Every amount from 1 to top - 1 is paid exactly with some of the coins held
    for amount in range(1, top):
        # pay[i] = number of coins of denomination i used to pay this amount (a separate payment per amount)
        pay = [model.int(0, top // d) for d in denominations]
        # a payment uses no more coins of a kind than are held
        for i in range(k):
            model.constraint(pay[i] <= x[i])
        # the coins used add up to the amount exactly
        model.constraint(model.sum(denominations[i] * pay[i] for i in range(k)) == amount)

    # Minimise the number of coins
    model.minimize(model.sum(x))
    return optimizer, {"x": x}
