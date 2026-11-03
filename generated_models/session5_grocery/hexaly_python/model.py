"""Grocery: prices in cents of the items whose sum and product (in dollars) both equal the total price."""
import hexaly.optimizer as hx


def build(instance):
    total, n = instance["total_price"], instance["num_items"]  # the total in cents, and how many items were bought
    # In cents, the n prices multiply to total * 100^(n-1): each price is cents / 100 and so is the total
    product = total * 100 ** (n - 1)
    # Each price divides the product, so only those divisors up to the total are possible prices; listing them
    # lets Hexaly search over a few dozen values instead of every price up to the total
    divisors = [d for d in range(1, total + 1) if product % d == 0]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # choice[i] picks the price of item i from the divisors, and prices[i] is that price in cents
    candidates = model.array(divisors)
    choice = [model.int(0, len(divisors) - 1) for _ in range(n)]
    prices = [model.at(candidates, c) for c in choice]

    # Added, the prices come to the total
    model.constraint(model.sum(prices) == total)
    # Multiplied (in dollars), they come to the same total
    model.constraint(model.prod(prices) == product)

    return optimizer, {"prices": prices}
