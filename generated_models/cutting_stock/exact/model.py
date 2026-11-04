# cutting_stock: an Exact (Python) model from DCP Rosetta.
# Download the `cutting_stock.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cutting_stock.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python cutting_stock.py cutting_stock.json

from exact import Exact


def create_model(instance):
    """Rolls of raw material are cut into rolls of several widths, following
    cutting patterns that each yield a given number of rolls of each width. Each
    width has a number of orders that must be met. Decide how many times each
    pattern is used so that the total number of raw rolls cut is as small as
    possible."""
    orders = instance["orders"]                 # orders[w]: the number of rolls of width w that must be cut
    pattern_yield = instance["num_rolls_width"] # pattern_yield[p][w]: rolls of width w that one raw roll gives when cut with pattern p
    n_patterns = instance["num_patterns"]       # the number of cutting patterns
    n_widths = len(instance["widths"])          # the number of roll widths

    solver = Exact()

    # Exact identifies its variables by name.
    # used[p] is the number of raw rolls cut with pattern p, from 0 to 100
    used = [f"used_{p}" for p in range(n_patterns)]
    for name in used:
        solver.addVariable(name, 0, 100)

    # For each width, the rolls of that width given by all patterns together meet its orders.
    for w in range(n_widths):
        solver.addConstraint(
            [(pattern_yield[p][w], used[p]) for p in range(n_patterns) if pattern_yield[p][w]],
            True, orders[w])

    # The total number of raw rolls cut, from 0 to 100 with each pattern.
    total = "total_rolls"
    solver.addVariable(total, 0, 100 * n_patterns)
    # The total is the sum of the uses of all patterns.
    solver.addConstraint([(1, name) for name in used] + [(-1, total)], True, 0, True, 0)

    # Cut as few raw rolls as possible.
    solver.setObjective([(1, total)], minimize=True)

    return solver, {"patterns_used": used, "min_rolls_cut": total}


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
