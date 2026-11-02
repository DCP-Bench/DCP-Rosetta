# chess_set: a Z3 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/chess_set.html
# Run it (after `pip install z3-solver numpy`) with:
#   python chess_set.py

import z3


def create_model(instance):
    """A joinery makes small and large boxwood chess sets from limited lathe hours and boxwood.
    Decide how many sets of each kind to make each week to maximize profit."""
    lathe_hours = 4 * 40                 # four lathes, 40 hours a week each
    boxwood_kg = 200                     # boxwood available per week
    small_lathe, large_lathe = 3, 2      # lathe hours per small / large set
    small_wood, large_wood = 1, 3        # kg of boxwood per small / large set
    small_profit, large_profit = 5, 20   # profit per small / large set

    # small_set and large_set are the numbers of small and large sets made per week
    small_set = z3.Int("small_set")
    large_set = z3.Int("large_set")
    # max_profit is the weekly profit
    max_profit = z3.Int("max_profit")

    # No set type is made more often than either resource allows on its own.
    max_small = min(lathe_hours // small_lathe, boxwood_kg // small_wood)
    max_large = min(lathe_hours // large_lathe, boxwood_kg // large_wood)
    solver = z3.Optimize()

    solver.add(small_set >= 0, small_set <= max_small, large_set >= 0, large_set <= max_large)

    # The boxwood used does not exceed the boxwood available.
    solver.add(small_wood * small_set + large_wood * large_set <= boxwood_kg)
    # The lathe hours used do not exceed the hours available.
    solver.add(small_lathe * small_set + large_lathe * large_set <= lathe_hours)
    # The profit is the profit of the small sets plus that of the large sets.
    solver.add(max_profit == small_profit * small_set + large_profit * large_set)

    # Maximize the profit.
    solver.maximize(max_profit)

    return solver, {"small_set": small_set, "large_set": large_set, "max_profit": max_profit}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
