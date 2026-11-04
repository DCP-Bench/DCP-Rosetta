# coin3_application: a Z3 (Python) model from DCP Rosetta.
# Download the `coin3_application.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/coin3_application.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python coin3_application.py coin3_application.json

import z3


def create_model(instance):
    """Find the minimum number of coins that allows one to pay exactly any amount
    smaller than a given maximum amount, using a given set of denominations."""
    denominations = instance["denominations"]   # denominations[i]: the value of a coin of type i
    max_amount = instance["max_amount_to_pay"]  # every amount below this must be payable
    n = len(denominations)                      # the number of coin types

    # x[i] is the number of coins of type i that are carried
    x = [z3.Int(f"x_{i}") for i in range(n)]
    # num_coins is the total number of coins carried
    num_coins = z3.Int("num_coins")

    solver = z3.Optimize()

    # No count exceeds max_amount, since a payment below it never needs more coins of one type.
    solver.add([z3.And(xi >= 0, xi <= max_amount) for xi in x])
    solver.add(z3.And(num_coins >= 0, num_coins <= max_amount))

    # The total is the sum of the counts of the coin types.
    solver.add(num_coins == z3.Sum(x))

    # Every amount from 1 to max_amount - 1 can be paid exactly from the coins carried.
    for amount in range(1, max_amount):
        # used[i] is the number of coins of type i in the payment of this amount
        used = [z3.Int(f"used_{amount}_{i}") for i in range(n)]
        # A payment uses no more coins of a type than the amount allows, and no more than are carried.
        solver.add([z3.And(used[i] >= 0, used[i] <= amount // denominations[i], used[i] <= x[i])
                    for i in range(n)])
        # The coins used add up to the amount.
        solver.add(z3.Sum([used[i] * denominations[i] for i in range(n)]) == amount)

    # Carry as few coins as possible.
    solver.minimize(num_coins)

    return solver, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
