# chess_set: a Choco-solver (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/chess_set.html
# Run it (after `pip install pychoco numpy`) with:
#   python chess_set.py

from pychoco.model import Model


def create_model(instance):
    """A joinery makes small and large boxwood chess sets. Decide how many of each to make each
    week so that the lathe hours and the boxwood are not exceeded and the profit is as large as
    possible."""
    lathe_hours = 4 * 40                 # four lathes, each with an operator working 40 hours a week
    boxwood_kg = 200                     # boxwood that can be obtained each week
    small_lathe, large_lathe = 3, 2      # lathe hours for one small set and for one large set
    small_wood, large_wood = 1, 3        # kg of boxwood for one small set and for one large set
    small_profit, large_profit = 5, 20   # profit from one small set and from one large set

    # The most small sets, and the most large sets, that the hours or the boxwood allow.
    max_small = min(lathe_hours // small_lathe, boxwood_kg // small_wood)
    max_large = min(lathe_hours // large_lathe, boxwood_kg // large_wood)

    model = Model()

    # small_set and large_set: the number of small and large sets made each week
    small_set = model.intvar(0, max_small, name="small_set")
    large_set = model.intvar(0, max_large, name="large_set")
    # max_profit: the profit made each week
    max_profit = model.intvar(0, max_small * small_profit + max_large * large_profit, name="max_profit")

    # The boxwood used does not exceed the boxwood available.
    model.scalar([small_set, large_set], [small_wood, large_wood], "<=", boxwood_kg).post()
    # The lathe hours used do not exceed the hours available.
    model.scalar([small_set, large_set], [small_lathe, large_lathe], "<=", lathe_hours).post()
    # The profit is that of the small sets plus that of the large sets.
    model.scalar([small_set, large_set], [small_profit, large_profit], "=", max_profit).post()

    # Maximize the profit.
    return model, {
        "small_set": small_set, "large_set": large_set, "max_profit": max_profit,
    }, {"objective": max_profit, "maximize": True}


if __name__ == "__main__":
    import numpy as np

    model, outputs, objective = create_model({})
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
