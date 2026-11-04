# session1_money_change: an Exact (Python) model from DCP Rosetta.
# Download the `session1_money_change.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_money_change.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python session1_money_change.py session1_money_change.json

from exact import Exact


def create_model(instance):
    """Alice has to give Bob some change. She has different types of coins of
    different values and a certain number of coins of each value. Compose the
    change from the available coins, using as few coins as possible."""
    amount = instance["amount"]               # the change to give Bob
    types = instance["types_of_coins"]        # types[i]: the value of coin type i
    available = instance["available_coins"]   # available[i]: how many coins of type i Alice has

    solver = Exact()

    # Exact identifies its variables by name.
    # coin_counts[i] is the number of coins of type i given to Bob. Alice cannot
    # give more coins of a type than she has.
    coin_counts = [f"coin_counts_{i}" for i in range(len(types))]
    for i, name in enumerate(coin_counts):
        solver.addVariable(name, 0, available[i])

    # The coins given add up to the amount.
    solver.addConstraint(list(zip(types, coin_counts)), True, amount, True, amount)

    # Use as few coins as possible.
    solver.setObjective([(1, name) for name in coin_counts], minimize=True)

    return solver, {"coin_counts": coin_counts}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
