# chess_set: a PyCSP3 model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/chess_set.html
# Run it (after `pip install pycsp3`, which also needs Java for its ACE solver) with:
#   python chess_set.py

from pycsp3 import *


def create_model(instance):
    """A joinery makes two sizes of boxwood chess sets. Each small set needs 3 lathe
    hours and 1 kg of boxwood and earns a profit of $5; each large set needs 2 lathe
    hours and 3 kg of boxwood and earns $20. Four lathes work 40 hours a week and 200 kg
    of boxwood can be obtained per week. Decide how many sets of each kind to make to
    maximise the weekly profit."""
    n_lathes = 4
    hours_per_lathe_week = 40
    lathe_hours = n_lathes * hours_per_lathe_week  # 160 lathe hours available per week
    boxwood_kg = 200                               # boxwood available per week

    small_lathe_hours = 3   # lathe hours needed for one small set
    large_lathe_hours = 2   # lathe hours needed for one large set
    small_boxwood_kg = 1    # boxwood needed for one small set
    large_boxwood_kg = 3    # boxwood needed for one large set
    small_profit = 5        # profit from one small set, in dollars
    large_profit = 20       # profit from one large set, in dollars

    # small_set: the number of small sets made per week; a set takes at least one lathe hour,
    # so there are at most lathe_hours of them
    small_set = Var(dom=range(lathe_hours + 1))

    # large_set: the number of large sets made per week, with the same bound
    large_set = Var(dom=range(lathe_hours + 1))

    # max_profit: the weekly profit from the sets made; a loose bound, since at most
    # lathe_hours sets fit and each earns at most large_profit
    max_profit = Var(dom=range(large_profit * lathe_hours + 1))

    satisfy(
        # The small and large sets together need no more lathe hours than are available.
        small_lathe_hours * small_set + large_lathe_hours * large_set <= lathe_hours,
        # The small and large sets together need no more boxwood than can be obtained.
        small_boxwood_kg * small_set + large_boxwood_kg * large_set <= boxwood_kg,
        # The profit is $5 per small set and $20 per large set.
        max_profit == small_profit * small_set + large_profit * large_set,
    )

    # Maximise the weekly profit.
    maximize(max_profit)

    return {"small_set": small_set, "large_set": large_set, "max_profit": max_profit}


if __name__ == "__main__":
    outputs = create_model({})
    if solve() is OPTIMUM:
        for name, variable in outputs.items():
            print(name, "=", value(variable))
    else:
        print("No solution:", status())
