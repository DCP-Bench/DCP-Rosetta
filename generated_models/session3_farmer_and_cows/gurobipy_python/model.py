# session3_farmer_and_cows: a Gurobi (Python) model from DCP Rosetta.
# Download the `session3_farmer_and_cows.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_farmer_and_cows.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python session3_farmer_and_cows.py session3_farmer_and_cows.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Farmer and cows: give each son the number of cows he is due, so that every son gets the same total milk from the cows 1 to num_cows."""
    num_cows = instance["num_cows"]          # the number of cows, numbered 1 up to num_cows
    num_sons = instance["num_sons"]          # the number of sons
    cows_per_son = instance["cows_per_son"]  # cows_per_son[s]: the number of cows son s is to get
    cows = range(num_cows)                   # cow i (counted from 0) is the cow numbered i + 1
    sons = range(num_sons)
    # Cow i gives milk equal to its number, i + 1.
    milk = [i + 1 for i in cows]
    # Each son gets an equal share of the total milk of all the cows. The // rounds down;
    # the instances here divide evenly.
    milk_per_son = sum(milk) // num_sons

    model = gp.Model("farmer_and_cows")

    # owns[i, s] is 1 when cow i goes to son s.
    owns = model.addVars(cows, sons, vtype=GRB.BINARY, name="owns")

    # Every cow goes to exactly one son.
    model.addConstrs((owns.sum(i, "*") == 1 for i in cows), name="cow")
    # Each son gets the number of cows the distribution gives him.
    model.addConstrs((owns.sum("*", s) == cows_per_son[s] for s in sons), name="count")
    # Each son's cows give the same total milk, milk_per_son.
    model.addConstrs((gp.quicksum(milk[i] * owns[i, s] for i in cows) == milk_per_son
                      for s in sons), name="milk")

    # cow_assignments[i] is the son (counted from 0) that cow i goes to.
    return model, {"cow_assignments": [gp.quicksum(s * owns[i, s] for s in sons) for i in cows]}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.Params.OutputFlag = 0  # no solver log
    model.optimize()

    if model.Status == GRB.OPTIMAL:  # a solution
        # a variable's value is var.X, an expression's is expr.getValue(); both read through LinExpr
        value = np.vectorize(lambda out: round(gp.LinExpr(out).getValue()))
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution, Gurobi status", model.Status)  # 3 infeasible, 4 infeasible or unbounded
