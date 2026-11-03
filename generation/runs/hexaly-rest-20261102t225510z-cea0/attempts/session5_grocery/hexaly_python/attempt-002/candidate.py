"""Grocery: prices in cents of the items whose sum and product (in dollars) both equal the total price."""
import hexaly.optimizer as hx


def build(instance):
    total, n = instance["total_price"], instance["num_items"]
    # In cents, the n prices multiply to total * 100^(n-1): each price is cents / 100 and so is the total
    product = total * 100 ** (n - 1)
    # Each price divides the product, so only those divisors up to the total are possible prices
    divisors = [d for d in range(1, total + 1) if product % d == 0]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # prices[i] is the price of item i in cents, picked from the divisors by a choice index
    candidates = model.array(divisors)
    choice = [model.int(0, len(divisors) - 1) for _ in range(n)]
    prices = [model.at(candidates, c) for c in choice]

    # Added, the prices come to the total
    model.constraint(model.sum(prices) == total)
    # Multiplied (in dollars), they come to the same total
    model.constraint(model.prod(prices) == product)

    return optimizer, {"prices": prices}
