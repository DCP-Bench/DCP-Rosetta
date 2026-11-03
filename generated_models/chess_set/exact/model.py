# chess_set: an Exact (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/chess_set.html
# Run it (after `pip install exact numpy`) with:
#   python chess_set.py

from exact import Exact


def create_model(instance):
    """A joinery makes small and large boxwood chess sets. Decide how many of each to make each
    week, within the lathe hours and the boxwood available, to maximise the profit."""
    lathe_hours = 4 * 40                  # four lathes, each with a 40 hour week
    boxwood_kg = 200                      # boxwood that can be obtained per week
    small_hours, large_hours = 3, 2       # lathe hours for one small set, and for one large set
    small_kg, large_kg = 1, 3             # boxwood for one small set, and for one large set
    small_profit, large_profit = 5, 20    # profit from one small set, and from one large set

    # The most sets of each kind that the lathe hours and the boxwood allow on their own.
    max_small = min(lathe_hours // small_hours, boxwood_kg // small_kg)
    max_large = min(lathe_hours // large_hours, boxwood_kg // large_kg)

    solver = Exact()

    # Exact identifies its variables by name.
    # small_set and large_set are the numbers of small and large sets made per week
    solver.addVariable("small_set", 0, max_small)
    solver.addVariable("large_set", 0, max_large)
    # max_profit is the profit per week
    solver.addVariable("max_profit", 0, max_small * small_profit + max_large * large_profit)

    # The boxwood used does not exceed the boxwood available.
    solver.addConstraint([(small_kg, "small_set"), (large_kg, "large_set")], False, 0, True, boxwood_kg)

    # The lathe hours used do not exceed the hours available.
    solver.addConstraint([(small_hours, "small_set"), (large_hours, "large_set")], False, 0, True, lathe_hours)

    # The profit is the profit of the small sets plus that of the large sets.
    solver.addConstraint([(1, "max_profit"), (-small_profit, "small_set"), (-large_profit, "large_set")],
                         True, 0, True, 0)

    # Maximise the weekly profit.
    solver.setObjective([(1, "max_profit")], minimize=False)

    return solver, {"small_set": "small_set", "large_set": "large_set", "max_profit": "max_profit"}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
