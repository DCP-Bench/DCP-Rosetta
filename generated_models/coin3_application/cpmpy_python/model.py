# coin3_application: a CPMpy model from DCP Rosetta.
# Download the `coin3_application.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/coin3_application.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python coin3_application.py coin3_application.json

import cpmpy as cp


def create_model(instance):
    """Find the minimum number of coins that allows one to pay exactly any amount
    smaller than a given maximum amount, using a given set of denominations."""
    denominations = instance["denominations"]   # denominations[i]: the value of a coin of type i
    max_amount = instance["max_amount_to_pay"]  # every amount below this must be payable
    n = len(denominations)

    # x[i] is the number of coins of type i that are carried; no payment below
    # max_amount can use more than max_amount coins of one type, so that bounds each count
    x = cp.intvar(0, max_amount, shape=n, name="x")
    # the total number of coins carried
    num_coins = cp.intvar(0, max_amount, name="num_coins")

    model = cp.Model()

    # The total is the sum over the coin types.
    model.add(num_coins == cp.sum(x))

    # Every amount from 1 to max_amount - 1 can be paid exactly from the coins carried.
    for amount in range(1, max_amount):
        # used[i] is the number of coins of type i in the payment of this amount
        used = cp.intvar(0, max_amount, shape=n, name=f"used_{amount}")
        # The coins used add up to the amount.
        model.add(cp.sum(used * denominations) == amount)
        # A payment uses no more coins of a type than are carried.
        model.add(used <= x)

    # Carry as few coins as possible.
    model.minimize(num_coins)

    return model, {"x": x}


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
