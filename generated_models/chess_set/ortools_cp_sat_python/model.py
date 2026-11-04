# chess_set: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/chess_set.html
# Run it (after `pip install ortools`) with:
#   python chess_set.py

from ortools.sat.python import cp_model


def create_model(instance):
    """A joinery makes small and large boxwood chess sets from limited lathe hours and boxwood.
    Decide how many sets of each kind to make each week to maximise profit."""
    lathe_hours = 4 * 40                 # four lathes, 40 hours a week each
    boxwood_kg = 200                     # boxwood available per week
    small_lathe, large_lathe = 3, 2      # lathe hours per small / large set
    small_wood, large_wood = 1, 3        # kg of boxwood per small / large set
    small_profit, large_profit = 5, 20   # profit per small / large set

    # Upper bounds: no set type can be made more often than either resource allows on its own.
    max_small = min(lathe_hours // small_lathe, boxwood_kg // small_wood)
    max_large = min(lathe_hours // large_lathe, boxwood_kg // large_wood)

    model = cp_model.CpModel()

    # small_set and large_set are the numbers of small and large sets made per week
    small_set = model.new_int_var(0, max_small, "small_set")
    large_set = model.new_int_var(0, max_large, "large_set")
    # max_profit is the weekly profit
    max_profit = model.new_int_var(0, max_small * small_profit + max_large * large_profit, "max_profit")

    # The boxwood used does not exceed the boxwood available.
    model.add(small_wood * small_set + large_wood * large_set <= boxwood_kg)
    # The lathe hours used do not exceed the hours available.
    model.add(small_lathe * small_set + large_lathe * large_set <= lathe_hours)
    # The profit is the profit of the small sets plus that of the large sets.
    model.add(max_profit == small_profit * small_set + large_profit * large_set)

    # Maximise the profit.
    model.maximize(max_profit)

    return model, {"small_set": small_set, "large_set": large_set, "max_profit": max_profit}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
