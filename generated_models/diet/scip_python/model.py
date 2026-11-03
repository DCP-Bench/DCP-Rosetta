# diet: a SCIP (Python) model from DCP Rosetta.
# Download the `diet.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/diet.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python diet.py diet.json

from pyscipopt import Model, quicksum

# The statement's table: NUTRIENTS[i][j] is the amount of nutrition type j in one
# serving of food i. Nutrition types, in order: calories, chocolate (ounces),
# sugar (ounces), fat (ounces). The table is part of the problem, not of the
# instance, so it is written out here.
NUTRIENTS = [
    [400, 3, 2, 2],  # chocolate cake, one slice
    [200, 2, 2, 4],  # chocolate ice cream, one scoop
    [150, 0, 4, 1],  # cola, one bottle
    [500, 0, 4, 5],  # pineapple cheesecake, one piece
]


def create_model(instance):
    """A diet is chosen for the least cost: buy whole servings of the foods so that
    each nutrition type reaches its required minimum."""
    n = instance["n"]            # n: the number of foods; the statement's table has four
    price = instance["price"]    # price[i]: the cost of one serving of food i
    limits = instance["limits"]  # limits[j]: the least amount of nutrition type j the diet must give

    model = Model("diet")

    # x[i] is the number of servings of food i in the diet: a whole number, at least 0.
    # The statement sets no upper limit on servings.
    x = [model.addVar(f"x_{i}", vtype="I", lb=0) for i in range(n)]

    # Each nutrition type must reach its minimum: the servings of all foods together
    # give at least limits[j] of nutrition type j.
    for j, limit in enumerate(limits):
        model.addCons(quicksum(NUTRIENTS[i][j] * x[i] for i in range(n)) >= limit)

    # cost is the total price of the servings bought, and it is what the diet minimises.
    cost = quicksum(price[i] * x[i] for i in range(n))
    model.setObjective(cost, "minimize")

    return model, {"cost": cost}


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
