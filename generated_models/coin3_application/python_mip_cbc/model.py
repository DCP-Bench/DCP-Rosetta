# coin3_application: a Python-MIP (Python) model from DCP Rosetta.
# Download the `coin3_application.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/coin3_application.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python coin3_application.py coin3_application.json

import mip


def create_model(instance):
    """Find the fewest coins that allow one to pay exactly every amount below a given
    maximum, using coins of the given denominations."""
    denominations = instance["denominations"]   # denominations[i]: the value of a coin of kind i
    max_amount = instance["max_amount_to_pay"]  # every amount from 1 up to this, excluding it, must be payable
    n_denominations = len(denominations)        # the number of coin kinds

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # x[i] is the number of coins of kind i to carry. Carrying more than (max_amount - 1) // denominations[i]
    # coins of one kind never helps, since no amount below max_amount needs that many.
    x = [
        model.add_var(f"x_{i}", lb=0, ub=(max_amount - 1) // denominations[i], var_type=mip.INTEGER)
        for i in range(n_denominations)
    ]

    # Every amount from 1 to max_amount - 1 can be paid exactly with the coins carried.
    for amount in range(1, max_amount):
        # y[i] is the number of coins of kind i used to pay this amount.
        y = [
            model.add_var(f"y_{amount}_{i}", lb=0, ub=amount // denominations[i], var_type=mip.INTEGER)
            for i in range(n_denominations)
        ]
        # The coins used add up to the amount.
        model += mip.xsum(denominations[i] * y[i] for i in range(n_denominations)) == amount
        # Only coins that are carried can be used.
        for i in range(n_denominations):
            model += y[i] <= x[i]

    # Carry as few coins as possible.
    model.objective = mip.xsum(x)

    return model, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
