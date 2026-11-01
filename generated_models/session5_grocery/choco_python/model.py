# session5_grocery: a Choco-solver (Python) model from DCP Rosetta.
# Download the `session5_grocery.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_grocery.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python session5_grocery.py session5_grocery.json

from pychoco.model import Model


def prime_factors(value):
    """Exponent of each prime in value, by trial division: {prime: exponent}."""
    factors = {}
    divisor = 2
    while divisor * divisor <= value:
        while value % divisor == 0:
            factors[divisor] = factors.get(divisor, 0) + 1
            value //= divisor
        divisor += 1
    if value > 1:
        factors[value] = factors.get(value, 0) + 1
    return factors


def create_model(instance):
    """A kid buys some items. The cashier multiplies the prices instead of adding them,
    and the product, read in dollars, comes to the same total as the sum. Find the price
    of each item, in cents."""
    total_price = instance["total_price"]  # the total price, in cents
    num_items = instance["num_items"]      # the number of items bought

    model = Model()

    # prices[i] is the price of item i, in cents
    prices = [model.intvar(1, total_price, name=f"prices_{i}") for i in range(num_items)]

    # The prices add up to the total.
    model.sum(prices, "=", total_price).post()

    # Read in cents, the product of the prices is the total times 100^(num_items - 1).
    product = total_price * 100 ** (num_items - 1)
    product_factors = prime_factors(product)  # exponent of each prime in the product
    primes = sorted(product_factors)

    # The possible prices are the divisors of the product, each with its exponent for every prime.
    divisor_rows = []
    for price in range(1, total_price + 1):
        if product % price == 0:
            exponents = []
            rest = price
            for p in primes:
                e = 0
                while rest % p == 0:
                    rest //= p
                    e += 1
                exponents.append(e)
            divisor_rows.append([price] + exponents)

    # exponents[i][k] is the exponent of primes[k] in the price of item i
    exponents = [[model.intvar(0, product_factors[p], name=f"exponent_{i}_{p}") for p in primes]
                 for i in range(num_items)]
    # Each price is a divisor of the product, with the matching exponents.
    for i in range(num_items):
        model.table([prices[i]] + exponents[i], divisor_rows).post()

    # For each prime, the exponents over all items add up to its exponent in the product,
    # so the prices multiply to the product.
    for k, p in enumerate(primes):
        model.sum([exponents[i][k] for i in range(num_items)], "=", product_factors[p]).post()

    return model, {"prices": prices}, None


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
