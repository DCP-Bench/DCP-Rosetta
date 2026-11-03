# prod: a Python-MIP (Python) model from DCP Rosetta.
# Download the `prod.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/prod.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python prod.py prod.json

import math

import mip


def create_model(instance):
    """Production planning: choose how many units of each product to make, at most the
    product's limit, so that the total profit is as large as possible while the time needed
    stays within the time available."""
    a = instance["a"]  # a[j]: one unit of product j takes 1 / a[j] of the time
    b = instance["b"]  # the time available
    c = instance["c"]  # c[j]: the profit per unit of product j
    u = instance["u"]  # u[j]: the most units of product j that can be made
    n_products = len(a)

    model = mip.Model(sense=mip.MAXIMIZE, solver_name="CBC")

    # x[j]: the number of units of product j to make
    x = [model.add_var(f"x_{j}", lb=0, ub=u[j], var_type=mip.INTEGER) for j in range(n_products)]

    # Range of the total profit: each product contributes between 0 and c[j] * u[j].
    min_profit = sum(min(0, c[j] * u[j]) for j in range(n_products))
    max_profit = sum(max(0, c[j] * u[j]) for j in range(n_products))

    # total_profit: the total profit of the units made
    total_profit = model.add_var("total_profit", lb=min_profit, ub=max_profit, var_type=mip.INTEGER)

    # scale: the least common multiple of the a[j]
    scale = math.lcm(*a)
    # The time needed for all units is at most the time available.
    model.add_constr(
        mip.xsum((scale // a[j]) * x[j] for j in range(n_products)) <= scale * b,
        name="time",
    )

    # The total profit is the profit per unit times the units made, summed over all products.
    model.add_constr(
        total_profit == mip.xsum(c[j] * x[j] for j in range(n_products)),
        name="profit",
    )

    # Maximise the total profit.
    model.objective = total_profit

    return model, {"total_profit": total_profit, "x": x}


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
