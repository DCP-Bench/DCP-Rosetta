# session5_grocery: an Exact (Python) model from DCP Rosetta.
# Download the `session5_grocery.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_grocery.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python session5_grocery.py session5_grocery.json

from exact import Exact


def prime_factors(n):
    """The primes that divide n."""
    primes = set()
    p = 2
    while p * p <= n:
        while n % p == 0:
            primes.add(p)
            n //= p
        p += 1
    if n > 1:
        primes.add(n)
    return primes


def exponent(n, p):
    """How many times the prime p divides n."""
    count = 0
    while n % p == 0:
        n //= p
        count += 1
    return count


def create_model(instance):
    """A kid buys several items. The cashier first multiplies the item prices and
    then adds them, and both give the same total price. Find the prices of the items, in cents."""
    total_price = instance["total_price"]  # the total price, in cents
    num_items = instance["num_items"]      # the number of items bought

    # Multiplying the prices gives the same total when read in dollars. In cents, the product is
    # the total price times 100 for each item after the first.
    product = total_price * 100 ** (num_items - 1)

    # The primes that divide the product.
    primes = prime_factors(product)
    # The prices that can occur: the divisors of the product that are at most the total price.
    candidates = [d for d in range(1, total_price + 1) if product % d == 0]

    solver = Exact()

    # Exact identifies its variables by name.
    # prices[i] is the price of item i, in cents, between 1 and the total price
    prices = [f"price_{i}" for i in range(num_items)]
    for name in prices:
        solver.addVariable(name, 1, total_price)

    # chosen[i][k] is 1 when item i costs candidates[k] cents, and 0 when not
    chosen = [[f"price_{i}_is_{d}" for d in candidates] for i in range(num_items)]
    for row in chosen:
        for name in row:
            solver.addVariable(name, 0, 1)

    # Each item costs exactly one of the candidate prices.
    for i in range(num_items):
        solver.addConstraint([(1, name) for name in chosen[i]], True, 1, True, 1)

    # The price of each item is the candidate price it costs.
    for i in range(num_items):
        solver.addConstraint([(d, chosen[i][k]) for k, d in enumerate(candidates)]
                             + [(-1, prices[i])], True, 0, True, 0)

    # Adding the prices gives the total price.
    solver.addConstraint([(1, name) for name in prices], True, total_price, True, total_price)

    # Multiplying the prices gives the product: for each prime, its powers in the prices add up
    # to its power in the product.
    for p in sorted(primes):
        target = exponent(product, p)
        solver.addConstraint(
            [(exponent(d, p), chosen[i][k]) for i in range(num_items)
             for k, d in enumerate(candidates) if exponent(d, p)],
            True, target, True, target)

    return solver, {"prices": prices}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
