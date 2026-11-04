# cutting_stock: a PuLP (Python) model from DCP Rosetta.
# Download the `cutting_stock.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cutting_stock.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python cutting_stock.py cutting_stock.json

import pulp


def create_model(instance):
    """Rolls of raw material are cut into rolls of several widths, following cutting
    patterns that each yield a given number of rolls of each width. Each width has a
    number of orders that must be met. Decide how many times to use each pattern so
    that the total number of raw rolls cut is as small as possible."""
    roll_width = instance["roll_width"]          # the width of a raw roll
    widths = instance["widths"]                  # widths[w]: the width of the rolls of kind w
    orders = instance["orders"]                  # orders[w]: the number of rolls of width w that must be cut
    pattern_yield = instance["num_rolls_width"]  # pattern_yield[p][w]: rolls of width w that one raw roll gives with pattern p
    n_patterns = instance["num_patterns"]        # the number of cutting patterns
    n_widths = len(widths)                       # the number of widths

    problem = pulp.LpProblem("cutting_stock", pulp.LpMinimize)

    # used[p] is the number of raw rolls cut with pattern p, at most 100
    used = [pulp.LpVariable(f"pattern_{p}", 0, 100, cat="Integer") for p in range(n_patterns)]

    # Every width gets at least as many rolls as it has orders.
    for w in range(n_widths):
        problem += pulp.lpSum(pattern_yield[p][w] * used[p] for p in range(n_patterns)) >= orders[w]

    # rolls is the total number of raw rolls cut.
    rolls = pulp.lpSum(used)
    # Minimize the total number of raw rolls cut.
    problem += rolls

    return problem, {"patterns_used": used, "min_rolls_cut": rolls}


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
