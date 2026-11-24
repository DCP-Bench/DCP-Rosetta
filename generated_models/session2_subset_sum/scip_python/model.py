# session2_subset_sum: a SCIP (Python) model from DCP Rosetta.
# Download the `session2_subset_sum.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_subset_sum.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python session2_subset_sum.py session2_subset_sum.json

from pyscipopt import Model, quicksum


def create_model(instance):
    """A bank van carried several kinds of coin bags, and each bag of a kind holds the
    same number of coins. Some bags were stolen, and together they held the total number
    of coins lost. Find how many bags of each kind were stolen. The data gives no limit
    on how many bags of one kind there were, so any count that fits the total is allowed."""
    # coin_numbers[i]: the number of coins in one bag of kind i
    coin_numbers = instance["coin_numbers"]
    # total: the number of coins lost, over all the stolen bags
    total = instance["total_coins_lost"]

    model = Model("session2_subset_sum")

    # bags[i] is the number of bags of kind i that were stolen. Each bag holds at least one
    # coin (an assumption about the data), and every stolen coin counts in the total, so
    # bags[i] * coin_numbers[i] <= total. The upper bound total // coin_numbers[i] is the
    # largest count that fits, and it is given as the variable's bound.
    bags = [
        model.addVar(name=f"bags_{i}", vtype="I", lb=0, ub=total // c)
        for i, c in enumerate(coin_numbers)
    ]

    # The stolen bags hold exactly the total number of coins lost.
    model.addCons(quicksum(c * b for c, b in zip(coin_numbers, bags)) == total)

    return model, {"bags": bags}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
