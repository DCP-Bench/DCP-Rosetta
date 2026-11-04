# prod: a Z3 (Python) model from DCP Rosetta.
# Download the `prod.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/prod.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python prod.py prod.json

import math

import z3


def create_model(instance):
    """Production: choose a quantity x[j] of each product j, between 0 and u[j], so that the
    total profit, the sum of c[j] * x[j], is as large as possible while the sum of
    x[j] / a[j] stays at most b."""
    a = instance["a"]  # a[j]: one unit of product j uses 1 / a[j] of the capacity
    c = instance["c"]  # c[j]: the profit per unit of product j
    u = instance["u"]  # u[j]: the most units of product j that can be made
    b = instance["b"]  # the capacity
    n_products = len(a)

    # x[j]: the number of units of product j made
    x = [z3.Int(f"x_{j}") for j in range(n_products)]

    solver = z3.Optimize()

    # Each product is made in a quantity from 0 up to its u[j].
    solver.add([z3.And(x[j] >= 0, x[j] <= u[j]) for j in range(n_products)])

    # The capacity used, the sum of x[j] / a[j], is at most b. Both sides are multiplied by
    # the least common multiple of the a[j], so that every term is a whole number.
    lcm = math.lcm(*a)
    solver.add(z3.Sum([(lcm // a[j]) * x[j] for j in range(n_products)]) <= b * lcm)

    # The total profit, to be as large as possible.
    total_profit = z3.Sum([c[j] * x[j] for j in range(n_products)])

    solver.maximize(total_profit)

    return solver, {"x": x, "total_profit": total_profit}


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
