# session1_money_change: a PyCSP3 model from DCP Rosetta.
# Download the `session1_money_change.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_money_change.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python session1_money_change.py session1_money_change.json

from pycsp3 import *


def create_model(instance):
    """Alice has to give Bob some change. She has different types of coins of different values and she has a certain
    number of coins of each value available. How can the change be composed with the available coins minimizing the
    number of coins used?"""
    amount = instance["amount"]                    # the change to give, in the unit of the coin values
    coin_values = instance["types_of_coins"]       # coin_values[i] is the value of a coin of type i
    available = instance["available_coins"]        # available[i] is the number of coins of type i Alice holds
    n_types = len(coin_values)

    # counts[i] is the number of coins of type i given to Bob; it cannot exceed the coins Alice holds.
    counts = VarArray(size=n_types, dom=lambda i: range(available[i] + 1))

    satisfy(
        # The coins given to Bob add up to the amount.
        Sum(coin_values[i] * counts[i] for i in range(n_types)) == amount,
    )

    # The number of coins used is to be minimal.
    minimize(Sum(counts))

    return {"coin_counts": counts}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is OPTIMUM:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())
