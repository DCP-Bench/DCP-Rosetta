# coin3_application: a hermax (Python) model from DCP Rosetta.
# Download the `coin3_application.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/coin3_application.html
# Then run it on the first instance (after `pip install hermax`):
#   python coin3_application.py coin3_application.json

from hermax.model import Model


def create_model(instance):
    """Choose how many coins of each denomination to carry, so that the total number of
    coins is as small as possible while every amount from 1 up to one less than the
    maximum amount to pay can be paid exactly with some of the carried coins."""
    denominations = instance["denominations"]   # denominations[i]: the value of coin kind i
    max_amount = instance["max_amount_to_pay"]  # every amount 1 .. max_amount - 1 must be payable
    n = len(denominations)

    m = Model()

    # x[i] is the number of coins of denomination i that we carry. Paying any amount below
    # max_amount never needs more than (max_amount - 1) // value coins of one kind, and
    # carrying more only costs, so that is the upper bound of x[i].
    x = [m.int(f"x_{i}", 0, (max_amount - 1) // denominations[i]) for i in range(n)]

    # For each amount v to pay, paid[v][i] is the number of coins of denomination i used
    # to pay exactly v. It is at most how many of that kind we carry, and at most v // value.
    for v in range(1, max_amount):
        paid = [m.int(f"paid_{v}_{i}", 0, min(x[i].ub, v // denominations[i])) for i in range(n)]

        # The coins used to pay v add up to exactly v.
        m &= (sum(denominations[i] * paid[i] for i in range(n)) == v)

        # Only coins we carry can be used: no more of a kind than is carried.
        for i in range(n):
            m &= (paid[i] <= x[i])

    # Minimise the total number of coins carried.
    m.obj += sum(x[i] for i in range(n))

    return m, {"x": x}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
