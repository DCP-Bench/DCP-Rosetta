# session5_grocery: a cvc5 (Python) model from DCP Rosetta.
# Download the `session5_grocery.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_grocery.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python session5_grocery.py session5_grocery.json

import cvc5.pythonic as c5


def create_model(instance):
    """A kid buys several items. The cashier first multiplies the item prices and
    then adds them, and both give the same total price. Find the prices of the items, in cents."""
    n_items = instance["num_items"]  # the number of items bought
    total = instance["total_price"]  # the total price, in cents

    # The product of the prices in cents. Multiplying the prices as dollars gives
    # the total, and each dollar is 100 cents, so each item after the first adds two zeros.
    product_total = total * 100 ** (n_items - 1)

    # Every partial product is at most product_total, so the products are wide
    # enough that none overflows.
    width = product_total.bit_length() + 1

    # Each price is at most the total. The spare bit keeps the top bit clear.
    price_width = total.bit_length() + 1

    # prices[i] is the price of item i, in cents
    prices = [c5.Int(f"price_{i}") for i in range(n_items)]
    # The same prices as fixed-width numbers, for the arithmetic below
    bits = [c5.BitVec(f"x{i}", price_width) for i in range(n_items)]

    solver = c5.Solver()

    # Each price is a positive amount, at most the total, and the two copies agree.
    for p, x in zip(prices, bits):
        solver.add(p >= 1)
        solver.add(p <= total)
        solver.add(x <= total)
        solver.add(p == c5.BV2Int(x, is_signed=False))

    # Adding the prices gives the total. The sum is wide enough for n_items prices.
    extra = max(1, n_items.bit_length())
    total_sum = c5.ZeroExt(extra, bits[0])
    for x in bits[1:]:
        total_sum = total_sum + c5.ZeroExt(extra, x)
    solver.add(total_sum == total)

    # Multiplying the prices gives product_total, one partial product at a time.
    product = c5.ZeroExt(width - price_width, bits[0])
    for i, x in enumerate(bits[1:], start=1):
        next_product = c5.BitVec(f"product_{i}", width)
        solver.add(c5.ZeroExt(width, product) * c5.ZeroExt(2 * width - price_width, x) == c5.ZeroExt(width, next_product))
        product = next_product
    solver.add(product == product_total)

    return solver, {"prices": prices}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
