# cutting_stock: a CPMpy model from DCP Rosetta.
# Download the `cutting_stock.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cutting_stock.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python cutting_stock.py cutting_stock.json

import numpy as np
import cpmpy as cp


def create_model(instance):
    """Rolls of raw material are cut into rolls of several widths, following
    cutting patterns that each yield a given number of rolls of each width. Each
    width has a number of orders that must be met. Decide how many times each
    pattern is used so that the total number of raw rolls cut is as small as
    possible."""
    orders = instance["orders"]                         # orders[w]: the number of rolls of width w that must be cut
    pattern_yield = np.array(instance["num_rolls_width"])  # pattern_yield[p][w]: rolls of width w that cutting a raw roll with pattern p gives
    num_patterns = instance["num_patterns"]             # the number of cutting patterns

    # used[p] is the number of raw rolls cut with pattern p (at most 100 each)
    used = cp.intvar(0, 100, shape=num_patterns, name="patterns_used")
    # The total number of raw rolls cut
    rolls = cp.intvar(0, 100 * num_patterns, name="min_rolls_cut")

    model = cp.Model()
    # For each width, the rolls cut with all patterns meet the orders.
    model.add(used @ pattern_yield >= orders)
    # The total number of raw rolls cut is the sum over the patterns.
    model.add(rolls == cp.sum(used))
    # Cut as few raw rolls as possible.
    model.minimize(rolls)

    return model, {"patterns_used": used, "min_rolls_cut": rolls}


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
