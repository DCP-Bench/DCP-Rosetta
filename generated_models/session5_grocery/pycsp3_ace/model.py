# session5_grocery: a PyCSP3 model from DCP Rosetta.
# Download the `session5_grocery.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_grocery.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python session5_grocery.py session5_grocery.json

from pycsp3 import *


def create_model(instance):
    """A kid buys some items. The cashier totals the prices by multiplying them instead of
    adding them, and gets the same total. Find the prices of n items, each a positive whole
    number of cents, such that the sum and the product of the prices, in dollars, both equal
    the total price in dollars."""
    n_items = instance["num_items"]  # the number of items bought
    total_price = instance["total_price"]  # the total price, in cents
    cents_per_dollar = 100  # 100 cents make a dollar

    # prices[i] is the price of item i in cents, a whole number from 1 up to the total: the
    # other prices are at least 1 cent each, so no price can exceed the total
    prices = VarArray(size=n_items, dom=range(1, total_price + 1))

    # The product of the prices in dollars is the product in cents divided by 100 once for each
    # of the n_items prices, which must equal total_price / 100, so the product in cents is
    # total_price * 100 ** (n_items - 1).
    product_cents = total_price * cents_per_dollar ** (n_items - 1)

    # Every product of whole-number prices divides product_cents, so the partial products take
    # only its divisors.
    sqrt_bound = int(product_cents ** 0.5)
    divisors = sorted({d for candidate in range(1, sqrt_bound + 1) if product_cents % candidate == 0 for d in (candidate, product_cents // candidate)})

    def product_bound(m):
        # m whole-number prices with a sum of at most total_price have a product of at most
        # (total_price / m) ** m (AM-GM); the share is rounded up, so the bound stays valid.
        share = (total_price + m - 1) // m
        return share ** m

    # partial[k] is the product in cents of the first k + 1 prices. It is bounded by product_bound
    # so that each multiplication stays under 2 ** 31: ACE 2.6 overflows its 32-bit bounds when
    # two large domains are multiplied.
    partial = VarArray(size=n_items - 1, dom=lambda k: [d for d in divisors if d <= product_bound(k + 1)])

    # The last product is a Table over the pairs (partial product, last price) that multiply to
    # product_cents, for the same overflow reason. ACE 2.6 also accepts invalid tuples for a Product
    # over four or more variables, which is why the product is split into binary steps.
    last_pairs = [(d, product_cents // d) for d in divisors if d <= product_bound(n_items - 1) and product_cents // d <= total_price]

    satisfy(
        # The prices add up to the total price in cents (the sum in dollars equals the total in dollars).
        Sum(prices) == total_price,
        # The first partial product is the first price.
        partial[0] == prices[0],
        # Each further partial product is the one before it times the next price.
        [partial[k] == partial[k - 1] * prices[k] for k in range(1, n_items - 1)],
        # The product of all the prices is product_cents (the product in dollars equals the total in dollars).
        Table(scope=[partial[n_items - 2], prices[n_items - 1]], supports=last_pairs),
    )

    return {"prices": prices}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())
