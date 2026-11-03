# prod: a SCIP (Python) model from DCP Rosetta.
# Download the `prod.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/prod.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python prod.py prod.json

from pyscipopt import Model, quicksum


def create_model(instance):
    """Choose how many units x[j] of each product j to make, as whole numbers
    from 0 up to u[j], so that the total profit, the sum of c[j] * x[j], is as
    large as possible while the sum of x[j] / a[j] stays at most b."""
    a = instance["a"]  # a[j]: x[j] is divided by a[j] in the limit, so a[j] is nonzero
    b = instance["b"]  # b: the most the sum of x[j] / a[j] may come to
    c = instance["c"]  # c[j]: the profit of each unit of product j
    u = instance["u"]  # u[j]: the most units of product j that can be made
    products = range(len(a))  # j runs over the products in the instance

    model = Model("prod")

    # x[j] is the number of units of product j to make: a whole number from 0
    # (the lower bound of the statement) up to u[j] (the bound from the instance)
    x = [model.addVar(f"x_{j}", vtype="I", lb=0, ub=u[j]) for j in products]

    # The limit: the sum of x[j] / a[j] over all products is at most b.
    # The coefficients 1 / a[j] are fractions, which SCIP takes as floats.
    model.addCons(quicksum(x[j] / a[j] for j in products) <= b)

    # total_profit is the sum of c[j] * x[j] over all products.
    total_profit = quicksum(c[j] * x[j] for j in products)

    # Maximise the total profit.
    model.setObjective(total_profit, "maximize")

    return model, {"total_profit": total_profit, "x": x}


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
