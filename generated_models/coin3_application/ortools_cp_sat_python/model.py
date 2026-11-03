# coin3_application: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `coin3_application.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/coin3_application.html
# Then run it on the first instance (after `pip install ortools`):
#   python coin3_application.py coin3_application.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Find the minimum number of coins that allows one to pay exactly any amount
    smaller than a given maximum amount, using a given set of denominations."""
    denominations = instance["denominations"]   # denominations[i]: the value of a coin of type i
    max_amount = instance["max_amount_to_pay"]  # every amount below this must be payable
    n_denominations = len(denominations)        # the number of coin types

    model = cp_model.CpModel()

    # x[i] is the number of coins of type i that are carried; no payment below
    # max_amount can use more than max_amount coins of one type, so that bounds each count
    x = [model.new_int_var(0, max_amount, f"x_{i}") for i in range(n_denominations)]
    # num_coins: the total number of coins carried
    num_coins = model.new_int_var(0, max_amount, "num_coins")
    # The total is the sum of the counts of the coin types.
    model.add(num_coins == sum(x))

    # Every amount from 1 to max_amount - 1 can be paid exactly from the coins carried.
    for amount in range(1, max_amount):
        # used[i] is the number of coins of type i in the payment of this amount
        used = [model.new_int_var(0, max_amount, f"used_{amount}_{i}") for i in range(n_denominations)]
        # The coins used add up to the amount.
        model.add(sum(denominations[i] * used[i] for i in range(n_denominations)) == amount)
        # A payment uses no more coins of a type than are carried.
        for i in range(n_denominations):
            model.add(used[i] <= x[i])

    # Carry as few coins as possible.
    model.minimize(num_coins)

    return model, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
