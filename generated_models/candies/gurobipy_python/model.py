# candies: a Gurobi (Python) model from DCP Rosetta.
# Download the `candies.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/candies.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python candies.py candies.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Give each child at least one candy, more candies than an immediate neighbour with a lower rating, and as few candies as possible in total."""
    ratings = instance["ratings"]  # ratings[i]: the rating score of child i, from their usual performance
    n = len(ratings)  # the number of children, sitting in a line
    children = range(n)

    model = gp.Model("candies")

    # x[i] is the number of candies child i gets. The lower bound 1 is from the statement; the upper bound n is not (the reference uses it to keep the variables finite).
    x = model.addVars(children, lb=1, ub=n, vtype=GRB.INTEGER, name="x")

    # If the child on the left has the higher rating, that child gets more candies than the one on the right.
    model.addConstrs((x[i - 1] >= x[i] + 1 for i in range(1, n) if ratings[i - 1] > ratings[i]), name="left_higher")
    # If the child on the right has the higher rating, that child gets more candies than the one on the left.
    model.addConstrs((x[i - 1] + 1 <= x[i] for i in range(1, n) if ratings[i - 1] < ratings[i]), name="right_higher")

    # z is the total number of candies, which Alice wants to minimise.
    z = x.sum()
    model.setObjective(z, GRB.MINIMIZE)

    return model, {"z": z, "x": [x[i] for i in children]}


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
