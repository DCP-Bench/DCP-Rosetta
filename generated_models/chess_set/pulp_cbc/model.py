# chess_set: a PuLP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/chess_set.html
# Run it (after `pip install pulp numpy`) with:
#   python chess_set.py

import pulp


def create_model(instance):
    """A small joinery makes small and large boxwood chess sets from limited lathe hours and
    boxwood. Decide how many sets of each kind to make each week to maximize profit."""
    lathe_hours = 4 * 40                # four lathes, 40 hours each a week
    boxwood_kg = 200                    # boxwood available each week
    small_lathe, large_lathe = 3, 2     # lathe hours for a small / large set
    small_wood, large_wood = 1, 3       # kg of boxwood for a small / large set
    small_profit, large_profit = 5, 20  # profit from a small / large set

    # No more sets of a kind can be made than either resource allows on its own.
    max_small = min(lathe_hours // small_lathe, boxwood_kg // small_wood)
    max_large = min(lathe_hours // large_lathe, boxwood_kg // large_wood)

    problem = pulp.LpProblem("chess_set", pulp.LpMaximize)

    # small_set and large_set are the numbers of small and large sets made per week
    small_set = pulp.LpVariable("small_set", 0, max_small, cat="Integer")
    large_set = pulp.LpVariable("large_set", 0, max_large, cat="Integer")
    # max_profit is the weekly profit
    max_profit = pulp.LpVariable(
        "max_profit", 0, max_small * small_profit + max_large * large_profit, cat="Integer"
    )

    # The boxwood used does not exceed the boxwood available.
    problem += small_wood * small_set + large_wood * large_set <= boxwood_kg
    # The lathe hours used do not exceed the hours available.
    problem += small_lathe * small_set + large_lathe * large_set <= lathe_hours
    # The profit is the profit of the small sets plus that of the large sets.
    problem += max_profit == small_profit * small_set + large_profit * large_set

    # Maximize the profit.
    problem += max_profit

    return problem, {"small_set": small_set, "large_set": large_set, "max_profit": max_profit}


if __name__ == "__main__":
    import numpy as np

    problem, outputs = create_model({})
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
