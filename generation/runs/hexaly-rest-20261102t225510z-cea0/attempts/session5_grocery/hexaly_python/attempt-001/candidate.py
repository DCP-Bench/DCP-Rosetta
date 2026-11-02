"""Grocery: prices in cents of the items whose sum and product (in dollars) both equal the total price."""
import hexaly.optimizer as hx


def build(instance):
    total, n = instance["total_price"], instance["num_items"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # prices[i] is the price of item i in cents; each is at least 1 and at most the total
    prices = [model.int(1, total) for _ in range(n)]

    # Added, the prices come to the total
    model.constraint(model.sum(prices) == total)
    # Multiplied, the prices in dollars come to the same total in dollars: with prices in cents,
    # the product of n prices is total * 100^(n-1), since each price is cents / 100 and the
    # total is cents / 100 as well
    model.constraint(model.prod(prices) == total * 100 ** (n - 1))

    return optimizer, {"prices": prices}
