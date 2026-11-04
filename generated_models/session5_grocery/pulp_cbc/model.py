# session5_grocery: a PuLP (Python) model from DCP Rosetta.
# Download the `session5_grocery.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_grocery.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python session5_grocery.py session5_grocery.json

import pulp


def create_model(instance):
    """A kid buys several items. The cashier first multiplies the item prices and
    then adds them, and both give the same total price. Find the prices of the items, in cents."""
    total_price = instance["total_price"]  # the total price, in cents
    n_items = instance["num_items"]  # the number of items bought

    # The product of the prices in cents. Multiplied in euros, the prices give the total price,
    # and each item after the first adds a factor of 100 in cents.
    product = total_price * 100 ** (n_items - 1)

    # A price is a whole number of cents, at most the total price, and it divides the product.
    candidates = [v for v in range(1, total_price + 1) if product % v == 0]

    # How many times the prime p divides number.
    def exponent(p, number):
        count = 0
        while number % p == 0:
            number //= p
            count += 1
        return count

    # The primes that divide the product.
    primes = []
    remaining = product
    p = 2
    while remaining > 1:
        if remaining % p == 0:
            primes.append(p)
            while remaining % p == 0:
                remaining //= p
        p += 1

    problem = pulp.LpProblem("session5_grocery", pulp.LpMinimize)  # no objective: any prices that fit are an answer

    # pick[i][v] is 1 when item i costs v cents.
    pick = {i: {v: pulp.LpVariable(f"pick_{i}_{v}", cat="Binary") for v in candidates}
            for i in range(n_items)}

    # prices[i] is the price of item i, in cents.
    prices = [pulp.LpVariable(f"price_{i}", 1, total_price, cat="Integer") for i in range(n_items)]

    # Each item costs exactly one of the candidate prices, and prices[i] is that price.
    for i in range(n_items):
        problem += pulp.lpSum(pick[i][v] for v in candidates) == 1
        problem += prices[i] == pulp.lpSum(v * pick[i][v] for v in candidates)

    # The prices add up to the total price.
    problem += pulp.lpSum(prices) == total_price

    # The prices multiply to the product when each prime divides them as often as it divides
    # the product. A price cannot have a prime that the product lacks, since it divides the product.
    for p in primes:
        problem += pulp.lpSum(exponent(p, v) * pick[i][v]
                              for i in range(n_items) for v in candidates) == exponent(p, product)

    return problem, {"prices": prices}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
