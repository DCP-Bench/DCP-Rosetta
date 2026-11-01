# cutting_stock: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `cutting_stock.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cutting_stock.html
# Then run it on the first instance (after `pip install ortools`):
#   python cutting_stock.py cutting_stock.json

from ortools.sat.python import cp_model


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

    model = cp_model.CpModel()

    # used[p] is the number of raw rolls cut with pattern p, at most 100
    used = [model.new_int_var(0, 100, f"p_{p}") for p in range(n_patterns)]

    # For each width, the rolls cut with all patterns reach its order.
    for w in range(n_widths):
        model.add(sum(pattern_yield[p][w] * used[p] for p in range(n_patterns)) >= orders[w])

    # The number of raw rolls cut is the sum over all patterns.
    n_rolls = sum(used)
    # Cut as few raw rolls as possible.
    model.minimize(n_rolls)

    return model, {"patterns_used": used, "min_rolls_cut": n_rolls}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
