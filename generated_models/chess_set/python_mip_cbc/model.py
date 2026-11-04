# chess_set: a Python-MIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/chess_set.html
# Run it (after `pip install mip numpy`) with:
#   python chess_set.py

import mip


def create_model(instance):
    """A joinery makes small and large boxwood chess sets from limited lathe hours and boxwood.
    Decide how many sets of each kind to make each week to maximize profit."""
    lathe_hours = 4 * 40                 # four lathes with skilled operators, each for a 40 hour week
    boxwood_kg = 200                     # boxwood that can be obtained per week
    small_lathe, large_lathe = 3, 2      # lathe hours per small set and per large set
    small_wood, large_wood = 1, 3        # kg of boxwood per small set and per large set
    small_profit, large_profit = 5, 20   # profit per small set and per large set

    # The most small and large sets that either resource allows on its own.
    max_small = min(lathe_hours // small_lathe, boxwood_kg // small_wood)
    max_large = min(lathe_hours // large_lathe, boxwood_kg // large_wood)

    model = mip.Model(sense=mip.MAXIMIZE, solver_name="CBC")

    # small_set and large_set are the numbers of small and large sets made per week
    small_set = model.add_var("small_set", var_type=mip.INTEGER, lb=0, ub=max_small)
    large_set = model.add_var("large_set", var_type=mip.INTEGER, lb=0, ub=max_large)
    # max_profit is the weekly profit
    max_profit = model.add_var(
        "max_profit", var_type=mip.INTEGER, lb=0, ub=max_small * small_profit + max_large * large_profit)

    # The boxwood used does not exceed the boxwood available.
    model += mip.xsum([small_wood * small_set, large_wood * large_set]) <= boxwood_kg

    # The lathe hours used do not exceed the hours available.
    model += mip.xsum([small_lathe * small_set, large_lathe * large_set]) <= lathe_hours

    # The profit is the profit of the small sets plus that of the large sets.
    model += max_profit == mip.xsum([small_profit * small_set, large_profit * large_set])

    # Maximize the weekly profit.
    model.objective = max_profit

    return model, {"small_set": small_set, "large_set": large_set, "max_profit": max_profit}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
