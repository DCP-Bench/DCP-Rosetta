# coin3_application: a PyCSP3 model from DCP Rosetta.
# Download the `coin3_application.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/coin3_application.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python coin3_application.py coin3_application.json

from pycsp3 import *


def create_model(instance):
    """Find the minimum number of coins that allows one to pay exactly any amount smaller
    than a given maximum amount, using a given set of denominations."""
    denominations = instance["denominations"]  # denominations[i]: the value of coin kind i
    max_amount_to_pay = instance["max_amount_to_pay"]  # every amount below this must be payable

    n_kinds = len(denominations)  # one kind of coin per denomination

    # every amount from 1 up to max_amount_to_pay - 1 must be paid exactly
    amounts = range(1, max_amount_to_pay)

    # x[i]: how many coins of kind i are bought; at most max_amount_to_pay - 1, the most coins
    # of one kind any amount below it can need
    x = VarArray(size=n_kinds, dom=range(max_amount_to_pay))

    # pay[a][i]: how many coins of kind i are used to pay exactly the amount a (rows 0 to
    # max_amount_to_pay - 1, so that row a is the amount a; row 0 is never used)
    pay = VarArray(size=[max_amount_to_pay, n_kinds], dom=range(max_amount_to_pay))

    satisfy(
        # Every amount a is paid exactly by the coins used for it.
        [Sum(pay[a][i] * denominations[i] for i in range(n_kinds)) == a for a in amounts],
        # The coins used for any amount are among the coins bought.
        [pay[a][i] <= x[i] for a in amounts for i in range(n_kinds)],
    )

    # Minimise the total number of coins bought.
    minimize(Sum(x))

    return {"x": x}


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
