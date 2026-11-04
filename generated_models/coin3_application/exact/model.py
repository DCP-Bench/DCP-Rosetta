# coin3_application: an Exact (Python) model from DCP Rosetta.
# Download the `coin3_application.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/coin3_application.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python coin3_application.py coin3_application.json

from exact import Exact


def create_model(instance):
    """Find the minimum number of coins that allows one to pay exactly any amount
    smaller than a given maximum amount, using a given set of denominations."""
    denominations = instance["denominations"]   # denominations[i]: the value of a coin of type i
    max_amount = instance["max_amount_to_pay"]  # every amount below this must be payable
    n = len(denominations)                      # the number of coin types

    solver = Exact()

    # Exact identifies its variables by name.
    # x[i] is the number of coins of type i that are carried. No payment below max_amount
    # needs more than max_amount coins of one type, so that bounds each count.
    x = [f"x_{i}" for i in range(n)]
    for name in x:
        solver.addVariable(name, 0, max_amount)

    # Every amount from 1 to max_amount - 1 can be paid exactly from the coins carried.
    for amount in range(1, max_amount):
        # used[i] is the number of coins of type i in the payment of this amount.
        used = [f"used_{amount}_{i}" for i in range(n)]
        for i in range(n):
            solver.addVariable(used[i], 0, max_amount)

            # The payment uses no more coins of a type than are carried.
            solver.addConstraint([(1, x[i]), (-1, used[i])], True, 0)

        # The coins used add up to the amount.
        solver.addConstraint([(denominations[i], used[i]) for i in range(n)], True, amount, True, amount)

    # The fewest coins carried in total.
    solver.setObjective([(1, name) for name in x], minimize=True)

    return solver, {"x": x}


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
