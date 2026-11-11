# prod: a Gurobi (Python) model from DCP Rosetta.
# Download the `prod.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/prod.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python prod.py prod.json

import math

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Production planning: choose how many units of each product to make, within each product's
    limit and within the budget, to maximise the total profit."""
    a = instance["a"]              # a[j] is the parameter of product j in the budget: one unit takes 1 / a[j] of it
    c = instance["c"]              # c[j] is the profit on each unit of product j
    u = instance["u"]              # u[j] is the most units of product j that can be made
    budget = instance["b"]         # the budget b: the total of (1 / a[j]) * units over all products must not exceed it
    products = range(len(a))

    model = gp.Model("prod")

    # x[j] is the number of units of product j to make, between 0 and u[j]. The statement does not say
    # the units are whole, but the output is an integer, so x[j] is an integer.
    x = model.addVars(products, lb=0, ub=u, vtype=GRB.INTEGER, name="x")

    # The budget: making x[j] units of product j takes x[j] / a[j] of it, and the total may not exceed b.
    # Multiplying both sides by lcm_a (the least common multiple of the a[j]) makes every coefficient
    # a whole number, so the check is exact rather than subject to rounding.
    lcm_a = math.lcm(*a)
    model.addConstr(gp.quicksum((lcm_a // a[j]) * x[j] for j in products) <= budget * lcm_a,
                    name="budget")

    # The total profit, to maximise: the sum of c[j] * x[j] over the products.
    total_profit = gp.quicksum(c[j] * x[j] for j in products)
    model.setObjective(total_profit, GRB.MAXIMIZE)

    # x is printed as a list, one entry per product; total_profit is printed as one number.
    return model, {"x": [x[j] for j in products], "total_profit": total_profit}


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
