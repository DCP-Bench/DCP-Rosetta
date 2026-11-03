# chess_set: a SCIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/chess_set.html
# Run it (after `pip install pyscipopt numpy`) with:
#   python chess_set.py

from pyscipopt import Model


def create_model(instance):
    """A joinery makes two sizes of boxwood chess sets each week. Decide how many
    small sets and how many large sets to make so that the weekly profit is as
    large as possible, within the lathe hours and the boxwood available.
    The instance file is empty ([]), so every number is fixed by the problem statement."""
    # The instance carries no data; these numbers come from the problem statement.
    lathes = 4                # four lathes, each with a skilled operator
    hours_per_lathe = 40      # each operator works a 40 hour week
    small_lathe_hours = 3     # lathe hours to machine one small set
    large_lathe_hours = 2     # lathe hours to machine one large set
    small_boxwood = 1         # kg of boxwood in one small set
    large_boxwood = 3         # kg of boxwood in one large set
    boxwood_per_week = 200    # kg of boxwood that can be obtained each week
    small_profit = 5          # dollars of profit per small set sold
    large_profit = 20         # dollars of profit per large set sold

    model = Model("chess_set")

    # small_set is the number of small sets made each week, a whole number.
    # Upper bound: boxwood alone allows at most 200 // 1 = 200 small sets.
    small_set = model.addVar("small_set", vtype="I", lb=0, ub=boxwood_per_week // small_boxwood)
    # large_set is the number of large sets made each week, a whole number.
    # Upper bound: boxwood alone allows at most 200 // 3 = 66 large sets.
    large_set = model.addVar("large_set", vtype="I", lb=0, ub=boxwood_per_week // large_boxwood)

    # The lathe hours used by the small and large sets are at most the 4 lathes x 40 hours = 160.
    model.addCons(small_lathe_hours * small_set + large_lathe_hours * large_set
                  <= lathes * hours_per_lathe)

    # The boxwood used by the small and large sets is at most the 200 kg available.
    model.addCons(small_boxwood * small_set + large_boxwood * large_set <= boxwood_per_week)

    # The weekly profit: $5 per small set plus $20 per large set.
    profit = small_profit * small_set + large_profit * large_set
    # Maximise the weekly profit.
    model.setObjective(profit, "maximize")

    outputs = {"small_set": small_set, "large_set": large_set, "max_profit": profit}
    return model, outputs


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
