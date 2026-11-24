# diet: a Gurobi (Python) model from DCP Rosetta.
# Download the `diet.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/diet.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python diet.py diet.json

import gurobipy as gp
from gurobipy import GRB

# Nutrients per unit of each food, from the table in the problem statement, in the
# order cake, ice cream, cola, cheesecake: calories, ounces of chocolate, ounces of
# sugar and ounces of fat.
CALORIES = [400, 200, 150, 500]
CHOCOLATE = [3, 2, 0, 0]
SUGAR = [2, 2, 4, 4]
FAT = [2, 4, 1, 5]


def create_model(instance):
    """Diet: buy whole units of four foods so that every nutritional minimum is met at the least cost."""
    price = instance["price"]    # price[f]: the price of one unit of food f
    limits = instance["limits"]  # the minimum calories, chocolate, sugar and fat the diet must give
    foods = range(instance["n"]) # the foods, numbered from 0 (there are four)

    model = gp.Model("diet")

    # units[f] is how many units of food f are bought.
    units = model.addVars(foods, lb=0, vtype=GRB.INTEGER, name="units")

    # Each nutrient reaches its minimum: calories, chocolate, sugar and fat in turn.
    for name, per_unit, minimum in zip(("calories", "chocolate", "sugar", "fat"),
                                       (CALORIES, CHOCOLATE, SUGAR, FAT), limits):
        model.addConstr(gp.quicksum(per_unit[f] * units[f] for f in foods) >= minimum, name=name)

    # cost is the total price of the diet. It is a variable of its own, so the declared output is one integer.
    cost = model.addVar(lb=0, vtype=GRB.INTEGER, name="cost")
    model.addConstr(cost == gp.quicksum(price[f] * units[f] for f in foods), name="price")

    # Minimise the cost of the diet.
    model.setObjective(cost, GRB.MINIMIZE)

    return model, {"cost": cost}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.Params.OutputFlag = 0  # no solver log
    model.Params.MIPGap = 0  # prove the optimum; the default stops within 0.01% of it
    model.optimize()

    if model.Status == GRB.OPTIMAL:  # a proven optimum
        print("Objective value:", round(model.ObjVal))
        # a variable's value is var.X, an expression's is expr.getValue(); both read through LinExpr
        value = np.vectorize(lambda out: round(gp.LinExpr(out).getValue()))
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution, Gurobi status", model.Status)  # 3 infeasible, 4 infeasible or unbounded
