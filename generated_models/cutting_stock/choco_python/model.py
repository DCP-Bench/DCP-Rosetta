# cutting_stock: a Choco-solver (Python) model from DCP Rosetta.
# Download the `cutting_stock.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cutting_stock.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python cutting_stock.py cutting_stock.json

from pychoco.model import Model


def create_model(instance):
    """Rolls of raw material are cut into rolls of several widths, following
    cutting patterns that each yield a given number of rolls of each width. Each
    width has a number of orders that must be met. Decide how many times each
    pattern is used so that the total number of raw rolls cut is as small as
    possible."""
    orders = instance["orders"]                      # orders[j]: the number of rolls of width j that must be cut
    rolls_per_pattern = instance["num_rolls_width"]  # rolls_per_pattern[p][j]: rolls of width j that one raw roll gives with pattern p
    n_patterns = instance["num_patterns"]            # the number of cutting patterns
    n_widths = len(orders)                           # the number of widths

    model = Model()

    # patterns_used[p] is the number of raw rolls cut with pattern p, at most 100
    patterns_used = [model.intvar(0, 100, name=f"patterns_used_{p}") for p in range(n_patterns)]

    # For each width, the rolls cut with all patterns reach its order.
    for j in range(n_widths):
        # the number of rolls of width j from each pattern
        coefficients = [rolls_per_pattern[p][j] for p in range(n_patterns)]
        model.scalar(patterns_used, coefficients, ">=", orders[j]).post()

    # min_rolls_cut is the total number of raw rolls cut, to be minimised.
    min_rolls_cut = model.intvar(0, 100 * n_patterns, name="min_rolls_cut")
    model.sum(patterns_used, "=", min_rolls_cut).post()

    return (
        model,
        {"patterns_used": patterns_used, "min_rolls_cut": min_rolls_cut},
        {"objective": min_rolls_cut, "maximize": False},
    )


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
