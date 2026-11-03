# session1_money_change: a CPMpy model from DCP Rosetta.
# Download the `session1_money_change.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_money_change.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python session1_money_change.py session1_money_change.json

import cpmpy as cp


def create_model(instance):
    """Alice gives Bob change using the coins she has available: compose the
    amount from the available coins, minimizing the number of coins used."""
    amount = instance["amount"]               # the change to give Bob
    types = instance["types_of_coins"]        # types[i]: the value of coin type i
    available = instance["available_coins"]   # available[i]: how many coins of type i Alice has

    # coin_counts[i] is the number of coins of type i given to Bob
    coin_counts = cp.intvar(0, max(available), shape=len(types), name="coin_counts")

    model = cp.Model()
    # The coins given add up to the amount.
    model.add(cp.sum(coin_counts * types) == amount)
    # Alice cannot give more coins of a type than she has.
    model.add(coin_counts <= available)
    # Use as few coins as possible.
    model.minimize(cp.sum(coin_counts))

    return model, {"coin_counts": coin_counts}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
