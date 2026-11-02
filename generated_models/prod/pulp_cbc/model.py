# prod: a PuLP (Python) model from DCP Rosetta.
# Download the `prod.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/prod.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python prod.py prod.json

import math

import pulp


def create_model(instance):
    """Production planning: choose quantities within per-product ceilings so that the shared
    production rate constraint holds, maximizing profit."""
    a = instance["a"]  # a[j]: one unit of product j takes 1 / a[j] of the production rate
    c = instance["c"]  # c[j]: the profit per unit of product j
    u = instance["u"]  # u[j]: the most units of product j that can be made
    b = instance["b"]  # the production rate available

    n_products = len(a)  # number of products

    problem = pulp.LpProblem("prod", pulp.LpMaximize)

    # x[j]: the units of product j made, from 0 up to u[j]
    x = [pulp.LpVariable(f"x{j}", 0, u[j], cat="Integer") for j in range(n_products)]

    # The rate used is sum of x[j] / a[j], at most b. Both sides are multiplied by the least
    # common multiple of the a[j], which keeps every coefficient a whole number.
    lcm_a = math.lcm(*a)
    problem += pulp.lpSum((lcm_a // a[j]) * x[j] for j in range(n_products)) <= b * lcm_a

    # total_profit: the profit of all units made, sum of c[j] * x[j]. Its upper bound is the
    # profit of making the most units of every product.
    profit_bound = sum(c[j] * u[j] for j in range(n_products))
    total_profit = pulp.LpVariable("total_profit", 0, profit_bound, cat="Integer")
    problem += total_profit == pulp.lpSum(c[j] * x[j] for j in range(n_products))

    # Maximise the total profit.
    problem += total_profit

    return problem, {"x": x, "total_profit": total_profit}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
