# cutting_stock: a Python-MIP (Python) model from DCP Rosetta.
# Download the `cutting_stock.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cutting_stock.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python cutting_stock.py cutting_stock.json

import mip


def create_model(instance):
    """Rolls of raw material are cut into rolls of several widths, following cutting
    patterns that each yield a given number of rolls of each width. Each width has a
    number of orders that must be met. Decide how many times each pattern is used so
    that the total number of raw rolls cut is as small as possible."""
    num_patterns = instance["num_patterns"]  # the number of cutting patterns
    yields = instance["num_rolls_width"]     # yields[p][w]: the number of rolls of width w that one raw roll gives with pattern p
    orders = instance["orders"]              # orders[w]: the number of rolls of width w that must be cut
    max_order = max(orders)                  # the largest order

    model = mip.Model(sense=mip.MINIMIZE)

    # used[p] is the number of raw rolls cut with pattern p; no pattern is used more often than the largest order
    used = [model.add_var(f"used_{p}", lb=0, ub=max_order, var_type=mip.INTEGER) for p in range(num_patterns)]

    # The total number of raw rolls cut
    total = model.add_var("total", lb=0, ub=num_patterns * max_order, var_type=mip.INTEGER)

    # The total is the sum of the patterns used.
    model.add_constr(total == mip.xsum(used))

    # For each width, the rolls cut with all patterns reach the order for that width.
    for w in range(len(orders)):
        model.add_constr(mip.xsum(yields[p][w] * used[p] for p in range(num_patterns)) >= orders[w])

    # Cut as few raw rolls as possible.
    model.objective = total

    return model, {"min_rolls_cut": total, "patterns_used": used}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
