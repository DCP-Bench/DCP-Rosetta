# cutting_stock: a Z3 (Python) model from DCP Rosetta.
# Download the `cutting_stock.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cutting_stock.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python cutting_stock.py cutting_stock.json

import z3


def create_model(instance):
    """Rolls of raw material are cut into rolls of several widths. Each cutting
    pattern gives a set number of rolls of each width from one raw roll. Each
    width has a number of orders that must be met. Decide how many raw rolls to
    cut with each pattern so that the number of raw rolls cut is as small as
    possible."""
    # roll_width: the width of a raw roll
    widths = instance["widths"]                  # widths[w]: the width of the rolls of kind w
    orders = instance["orders"]                  # orders[w]: the number of rolls of width w that must be cut
    pattern_yield = instance["num_rolls_width"]  # pattern_yield[p][w]: rolls of width w that one raw roll gives with pattern p
    n_patterns = instance["num_patterns"]        # the number of cutting patterns
    n_widths = len(widths)                       # the number of widths

    # used[p] is the number of raw rolls cut with pattern p
    used = [z3.Int(f"used_{p}") for p in range(n_patterns)]

    solver = z3.Optimize()

    # No pattern is cut a negative number of times, or more than 100 times.
    solver.add([u >= 0 for u in used] + [u <= 100 for u in used])

    # For each width, the rolls cut with all patterns reach its order.
    for w in range(n_widths):
        solver.add(z3.Sum([pattern_yield[p][w] * used[p] for p in range(n_patterns)]) >= orders[w])

    # The total number of raw rolls cut, summed over the patterns. It is minimized.
    n_rolls = z3.Sum(used)
    solver.minimize(n_rolls)

    return solver, {"patterns_used": used, "min_rolls_cut": n_rolls}


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
