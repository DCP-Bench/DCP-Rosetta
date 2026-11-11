# cutting_stock: a PyCSP3 model from DCP Rosetta.
# Download the `cutting_stock.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cutting_stock.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python cutting_stock.py cutting_stock.json

from pycsp3 import *


def create_model(instance):
    """This is a cutting stock problem. Raw rolls have a width roll_width, and pieces of several
    smaller widths are cut from them: orders[i] pieces of width widths[i] are needed. There are
    num_patterns cutting patterns, and cutting one raw roll with pattern i yields
    num_rolls_width[i][j] pieces of width widths[j]. The problem aims to minimize the total number
    of raw rolls cut, while at least the ordered number of pieces of each width is produced.
    How many rolls should be cut using each pattern?"""
    num_patterns = instance["num_patterns"]        # the number of cutting patterns
    num_rolls_width = instance["num_rolls_width"]  # num_rolls_width[i][j]: pieces of width widths[j] that one roll cut with pattern i yields
    orders = instance["orders"]                    # orders[j]: the pieces of width widths[j] that are needed
    n_widths = len(orders)
    # roll_width and widths are not read: the patterns already give the pieces each roll yields.

    # Taken as a bound: in an optimal cutting every roll covers at least one ordered piece (a roll
    # that covers none could be dropped), so there are at most sum(orders) rolls in all, and no
    # pattern is used more often than that.
    max_rolls = sum(orders)

    # patterns_used[i] is the number of rolls cut with pattern i
    patterns_used = VarArray(size=num_patterns, dom=range(max_rolls + 1))

    # min_rolls_cut is the total number of raw rolls cut
    min_rolls_cut = Var(dom=range(max_rolls + 1))

    satisfy(
        # Each width is produced at least as often as it is ordered: the rolls of every pattern,
        # times the pieces of that width the pattern yields, cover the order.
        [
            Sum(num_rolls_width[i][j] * patterns_used[i] for i in range(num_patterns)) >= orders[j]
            for j in range(n_widths)
        ],
        # The total number of rolls is the sum of the rolls cut with each pattern.
        min_rolls_cut == Sum(patterns_used),
    )

    # Minimise the total number of raw rolls cut.
    minimize(min_rolls_cut)

    return {"patterns_used": patterns_used, "min_rolls_cut": min_rolls_cut}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is OPTIMUM:
        print("patterns_used", "=", values(outputs["patterns_used"]))
        print("min_rolls_cut", "=", value(outputs["min_rolls_cut"]))
    else:
        print("No solution:", status())
