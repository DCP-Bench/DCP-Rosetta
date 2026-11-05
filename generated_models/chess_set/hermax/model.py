# chess_set: a hermax (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/chess_set.html
# Run it (after `pip install hermax`) with:
#   python chess_set.py

from hermax.model import Model


def create_model(instance):
    """A joinery makes two sizes of boxwood chess sets, a small one and a large one.
    Decide how many of each to make in a week so that the profit is as large as possible,
    within four lathes of 40 hours each (160 lathe-hours) and 200 kg of boxwood.
    The problem data is fixed by the statement, so the instance is not read."""
    # The problem data, as the statement gives it:
    lathe_hours = 160       # lathe-hours available per week (4 lathes x 40 hours)
    wood_kg = 200           # kg of boxwood available per week
    small_lathe = 3         # lathe-hours for one small set
    large_lathe = 2         # lathe-hours for one large set
    small_wood = 1          # kg of boxwood for one small set
    large_wood = 3          # kg of boxwood for one large set
    small_profit = 5        # profit from one small set, in dollars
    large_profit = 20       # profit from one large set, in dollars

    m = Model()

    # Upper bounds for each count, from the resource that runs out first.
    small_max = min(lathe_hours // small_lathe, wood_kg // small_wood)   # 53
    large_max = min(lathe_hours // large_lathe, wood_kg // large_wood)   # 66

    # small_set: the number of small chess sets made per week
    small_set = m.int("small_set", 0, small_max)
    # large_set: the number of large chess sets made per week
    large_set = m.int("large_set", 0, large_max)
    # max_profit: the weekly profit, in dollars, from the two counts
    max_profit = m.int("max_profit", 0, small_profit * small_max + large_profit * large_max)

    # The profit is exactly what the two kinds of set earn.
    m &= (max_profit == small_profit * small_set + large_profit * large_set)

    # The lathe-hours used by the sets do not exceed the 160 lathe-hours available.
    m &= (small_lathe * small_set + large_lathe * large_set <= lathe_hours)

    # The boxwood used by the sets does not exceed the 200 kg that can be obtained.
    m &= (small_wood * small_set + large_wood * large_set <= wood_kg)

    # Maximise the weekly profit (the solver minimises, so minimise its negative).
    m.obj += -max_profit

    # The objective in the problem's terms: the weekly profit, whose negation the solver minimises.
    return m, {
        "small_set": small_set,
        "large_set": large_set,
        "max_profit": max_profit,
    }, max_profit


if __name__ == "__main__":
    model, outputs, objective = create_model({})
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
        print("objective =", result[objective])
    else:
        print("No solution:", result.status)
