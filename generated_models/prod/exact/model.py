# prod: an Exact (Python) model from DCP Rosetta.
# Download the `prod.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/prod.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python prod.py prod.json

from math import gcd

from exact import Exact


def create_model(instance):
    """Choose how much of each product to make: between 0 and its limit u[j], so that the
    total profit, the sum of c[j] * x[j], is as large as possible while the sum of
    x[j] / a[j] stays at most b."""
    a = instance["a"]  # a[j]: product j uses 1 / a[j] of the shared capacity per unit made
    c = instance["c"]  # c[j]: the profit per unit of product j
    u = instance["u"]  # u[j]: the most units of product j that can be made
    b = instance["b"]  # the shared capacity
    n_products = len(a)

    solver = Exact()

    # Exact identifies its variables by name.
    # x[j] is the number of units of product j made, from 0 up to u[j]
    x = [f"x{j}" for j in range(n_products)]
    for j, name in enumerate(x):
        solver.addVariable(name, 0, u[j])

    # scale is the least common multiple of the a[j], so that each a[j] divides it.
    scale = 1
    for value in a:
        scale = scale // gcd(scale, value) * value

    # The capacity used, the sum of x[j] / a[j], is at most b. Both sides are multiplied by scale to keep whole numbers.
    solver.addConstraint([(scale // a[j], x[j]) for j in range(n_products)],
                         False, 0, True, b * scale)

    # total_profit is the sum of c[j] * x[j]; it is at most the profit of making every u[j].
    solver.addVariable("total_profit", 0, sum(c[j] * u[j] for j in range(n_products)))
    solver.addConstraint(list(zip(c, x)) + [(-1, "total_profit")], True, 0, True, 0)

    # Maximise the total profit.
    solver.setObjective([(1, "total_profit")], minimize=False)

    return solver, {"x": x, "total_profit": "total_profit"}


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
