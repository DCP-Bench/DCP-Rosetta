# coin3_application: a SCIP (Python) model from DCP Rosetta.
# Download the `coin3_application.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/coin3_application.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python coin3_application.py coin3_application.json

from pyscipopt import Model
import numpy as np


def create_model(instance):
    """Carry the fewest coins that let one pay every amount from 1 up to
    max_amount_to_pay - 1. Choose how many coins of each denomination to carry; each
    amount is paid with its own selection of coins, taken from the carried ones.
    The number of coins carried in total is minimised."""
    denominations = np.array(instance["denominations"])  # d[i]: the value of one coin of type i
    max_amount = instance["max_amount_to_pay"]  # every amount below this must be payable
    amounts = np.arange(1, max_amount)  # the amounts to pay: 1 .. max_amount - 1, one row each

    model = Model("coin3_application")

    # x[i] is the number of coins of type i carried (the output). Its upper bound
    # (max_amount - 1) // d[i] is derived, not given: an amount below max_amount uses at
    # most that many coins of type i, and an optimal carrying holds no more coins of
    # type i than the most any amount uses, since a spare coin could be dropped.
    x = model.addMatrixVar((len(denominations),), vtype="I", lb=0,
                           ub=(max_amount - 1) // denominations)

    # y[a, i] is the number of coins of type i used to pay the amount amounts[a].
    # Its upper bound amounts[a] // d[i] follows from the payment constraint below,
    # since every coin used adds its value to the amount paid.
    y = model.addMatrixVar((len(amounts), len(denominations)), vtype="I", lb=0,
                           ub=amounts[:, None] // denominations[None, :])

    # Each amount is paid exactly: the coins used for it add up to that amount.
    model.addMatrixCons((y * denominations).sum(axis=1) == amounts)

    # The coins used for any amount are among the coins carried.
    model.addMatrixCons(y <= x)

    # Minimise the total number of coins carried.
    model.setObjective(x.sum(), "minimize")

    return model, {"x": x}


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
