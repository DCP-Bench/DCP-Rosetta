# session5_grocery: a Z3 (Python) model from DCP Rosetta.
# Download the `session5_grocery.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_grocery.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python session5_grocery.py session5_grocery.json

import z3


def create_model(instance):
    """A kid buys several items. The cashier multiplies the item prices instead of adding
    them, and the product comes to the same total price as the sum. Find the prices of the
    items, in cents."""
    total_price = instance["total_price"]  # the total price, in cents
    num_items = instance["num_items"]      # the number of items bought

    # prices[i] is the price of item i, in cents
    prices = [z3.Int(f"prices_{i}") for i in range(num_items)]

    solver = z3.Solver()

    # The prices add up to the total price.
    solver.add(z3.Sum(prices) == total_price)

    # Multiplying the prices in dollars gives the total in dollars. In cents, each item
    # beyond the first adds a factor of 100 cents per dollar, so the product of the prices
    # is the total times 100 for each such item.
    product_target = total_price * 100 ** (num_items - 1)
    solver.add(z3.Product(prices) == product_target)

    # Each price is at least 1 cent and at most the total price.
    solver.add([z3.And(p >= 1, p <= total_price) for p in prices])

    # The most one item can cost: the total price less 1 cent for each other item.
    max_price = total_price - (num_items - 1)
    # The whole-cent amounts up to that cap that divide the product target. Each price
    # divides the product of all the prices, so each price is one of them.
    divisors = [d for d in range(1, max(max_price, 1) + 1) if product_target % d == 0]
    solver.add([z3.Or([p == d for d in divisors]) for p in prices])

    return solver, {"prices": prices}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
