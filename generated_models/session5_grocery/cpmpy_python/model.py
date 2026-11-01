# session5_grocery: a CPMpy model from DCP Rosetta.
# Download the `session5_grocery.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_grocery.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python session5_grocery.py session5_grocery.json

import numpy as np
import cpmpy as cp


def create_model(instance):
    """A kid buys several items. The cashier first multiplies the item prices and
    then adds them, and both give the same total price. Find the prices of the items, in cents."""
    total = instance["total_price"]  # the total price, in cents
    num_items = instance["num_items"]  # the number of items bought

    # prices[i] is the price of item i, in cents (at most the total, as the others cost at least 1)
    prices = cp.intvar(1, total, shape=num_items, name="prices")

    model = cp.Model()
    # Adding the prices gives the total.
    model.add(cp.sum(prices) == total)
    # Multiplying the prices gives the total too. Multiplying prices in dollars gives the
    # total in dollars; in cents the product is 100^num_items times larger and the total
    # 100 times larger, so the product equals total * 100^(num_items - 1).
    model.add(np.prod(prices) == total * 100 ** (num_items - 1))

    return model, {"prices": prices}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
