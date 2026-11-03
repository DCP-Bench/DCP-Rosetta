# prod: a CPMpy model from DCP Rosetta.
# Download the `prod.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/prod.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python prod.py prod.json

import cpmpy as cp
import numpy as np


def create_model(instance):
    """Choose a production quantity x[j] between 0 and u[j] for each element j of P,
    so that the total profit, the sum of c[j] * x[j], is as large as possible, while the
    sum of x[j] / a[j] stays at most b."""
    a = np.array(instance["a"])  # a[j]: the capacity use per unit of x[j] is 1 / a[j]
    c = np.array(instance["c"])  # c[j]: the profit per unit of x[j]
    u = np.array(instance["u"])  # u[j]: the upper limit on x[j]
    b = instance["b"]            # the most the weighted sum of x may reach

    # x[j] is the quantity produced for element j
    x = cp.intvar(0, max(u), shape=len(a), name="x")
    # total_profit is the sum of c[j] * x[j]
    profit = cp.sum(x * c)
    total_profit = cp.intvar(*profit.get_bounds(), name="total_profit")

    model = cp.Model()
    # The sum of x[j] / a[j] is at most b. Multiplying both sides by the least common
    # multiple of the a[j] keeps the arithmetic integer.
    lcm = int(np.lcm.reduce(a))
    model.add(cp.sum(x * (lcm // a)) <= b * lcm)
    # Each quantity stays within its own limit.
    model.add(x <= u)
    # total_profit holds the profit of the chosen quantities.
    model.add(total_profit == profit)
    # Make the total profit as large as possible.
    model.maximize(total_profit)

    return model, {"x": x, "total_profit": total_profit}


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
