# chess_set: a PySAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/chess_set.html
# Run it (after `pip install "python-sat[pblib]" numpy`) with:
#   python chess_set.py

from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """A joinery makes small and large boxwood chess sets from its lathe hours and boxwood,
    and decides how many of each to make each week to maximise profit."""
    lathe_hours = 4 * 40                         # four lathes, each run for a 40 hour week
    boxwood_kg = 200                             # boxwood that can be obtained each week
    small_lathe_hours, large_lathe_hours = 3, 2  # lathe hours per small and per large set
    small_boxwood, large_boxwood = 1, 3          # kg of boxwood per small and per large set
    small_profit, large_profit = 5, 20           # profit per small and per large set
    max_sets = 100                               # the largest count of each size the model considers

    pool = IDPool()

    # small_set and large_set are the numbers of small and large sets made each week
    small_set = Integer("small_set", 0, max_sets, encoding="coupled", vpool=pool)
    large_set = Integer("large_set", 0, max_sets, encoding="coupled", vpool=pool)
    # max_profit is the profit of the week
    max_profit = Integer("max_profit", 0, max_sets * (small_profit + large_profit), vpool=pool)
    engine = IntegerEngine(vars=[small_set, large_set, max_profit], vpool=pool)

    # The boxwood used by the sets made is no more than the boxwood obtainable.
    engine.add_linear(small_boxwood * small_set + large_boxwood * large_set <= boxwood_kg)
    # The lathe hours used by the sets made are no more than the hours available.
    engine.add_linear(small_lathe_hours * small_set + large_lathe_hours * large_set
                      <= lathe_hours)

    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    # The profit of the week is the profit of the sets made, given for each pair of counts.
    for a in range(max_sets + 1):
        for b in range(max_sets + 1):
            formula.append([-small_set.equals(a), -large_set.equals(b),
                            max_profit.equals(small_profit * a + large_profit * b)])

    # Maximise the profit. Each count from 1 to max_sets that the number of small sets falls
    # short of costs the profit of one small set, and likewise for large sets, so the cost is
    # the profit lost against making max_sets of each.
    for v in range(1, max_sets + 1):
        formula.append([small_set.ge(v)], weight=small_profit)
        formula.append([large_set.ge(v)], weight=large_profit)

    return formula, {"small_set": small_set, "large_set": large_set,
                     "max_profit": max_profit}


if __name__ == "__main__":
    import numpy as np
    from pysat.examples.rc2 import RC2Stratified

    formula, outputs = create_model({})

    # falsify as little soft-clause weight as possible
    model = RC2Stratified(formula).compute()

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
