# session1_money_change: a Gurobi (Python) model from DCP Rosetta.
# Download the `session1_money_change.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_money_change.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python session1_money_change.py session1_money_change.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Money change: pay the amount exactly from the coins available, using as few coins as possible."""
    values = instance["types_of_coins"]      # values[i]: the value of one coin of type i
    available = instance["available_coins"]  # available[i]: how many coins of type i Alice has
    amount = instance["amount"]              # the amount of change Alice gives Bob, in the same units as the values
    kinds = range(len(values))

    model = gp.Model("money_change")

    # coin_counts[i] is how many coins of type i Alice gives Bob: none up to all the ones she has of that type.
    coin_counts = model.addVars(kinds, lb=0, ub=available, vtype=GRB.INTEGER, name="coin_counts")

    # The coins given add up to the amount owed.
    model.addConstr(gp.quicksum(values[i] * coin_counts[i] for i in kinds) == amount, name="amount")

    # Minimise the number of coins given.
    model.setObjective(coin_counts.sum(), GRB.MINIMIZE)

    return model, {"coin_counts": list(coin_counts.values())}


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
