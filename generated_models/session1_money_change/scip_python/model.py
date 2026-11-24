# session1_money_change: a SCIP (Python) model from DCP Rosetta.
# Download the `session1_money_change.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_money_change.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python session1_money_change.py session1_money_change.json

from pyscipopt import Model, quicksum


def create_model(instance):
    """Alice has to give Bob some change worth exactly `amount`, using only the
    coins she has: a number of coins of each type, no more than she has of that
    type. The change must use as few coins as possible."""
    amount = instance["amount"]              # the sum of money Alice gives Bob, in the same unit as the coin values
    values = instance["types_of_coins"]      # values[j]: the value of one coin of type j
    available = instance["available_coins"]  # available[j]: how many coins of type j Alice has

    model = Model("session1_money_change")

    # coins[j] is the number of coins of type j that Alice gives Bob. It is a whole number,
    # at least 0 (lb=0: no negative counts), and at most the number Alice has of that type
    # (ub taken from available_coins).
    coins = [model.addVar(f"coins_{j}", vtype="I", lb=0, ub=count)
             for j, count in enumerate(available)]

    # The coins given to Bob are worth exactly the amount.
    model.addCons(quicksum(value * c for value, c in zip(values, coins)) == amount)

    # Minimise the total number of coins given to Bob.
    model.setObjective(quicksum(coins), "minimize")

    return model, {"coin_counts": coins}


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
