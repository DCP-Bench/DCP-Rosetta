# session2_subset_sum: a Gurobi (Python) model from DCP Rosetta.
# Download the `session2_subset_sum.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_subset_sum.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python session2_subset_sum.py session2_subset_sum.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """A bank van had several kinds of coin bag, each holding a set number of coins, and
    thieves stole some of the bags (there are many bags of each kind). A total number of coins
    was lost. Find how many bags of each kind were stolen."""
    total = instance["total_coins_lost"]  # the total number of coins lost
    coins = instance["coin_numbers"]  # coins[i]: the number of coins in a bag of kind i
    kinds = range(len(coins))  # the kinds of bag, numbered 0 to len(coins) - 1

    model = gp.Model("subset_sum")

    # bags[i] is the number of bags of kind i stolen. The upper bound total is not from the
    # statement: it keeps the variables finite, and the reference uses it.
    bags = model.addVars(kinds, lb=0, ub=total, vtype=GRB.INTEGER, name="bags")

    # The coins in the stolen bags add up to exactly the total number of coins lost.
    model.addConstr(gp.quicksum(coins[i] * bags[i] for i in kinds) == total, name="total")

    # No objective: any choice of stolen bags that loses exactly the total is a solution.

    return model, {"bags": [bags[i] for i in kinds]}


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
