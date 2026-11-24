# coin3_application: a Gurobi (Python) model from DCP Rosetta.
# Download the `coin3_application.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/coin3_application.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python coin3_application.py coin3_application.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Coin set: the fewest coins from which every amount below the maximum can be paid exactly."""
    denominations = instance["denominations"]  # denominations[i]: the value of coin kind i
    top = instance["max_amount_to_pay"]        # the maximum amount: every amount below it must be payable
    kinds = range(len(denominations))
    amounts = range(1, top)

    model = gp.Model("coin3_application")

    # x[i] is how many coins of denomination i are in the set.
    # The bound top on each x[i] is not in the statement: it is the reference model's
    # bound, kept so that the variables are finite.
    x = model.addVars(kinds, lb=0, ub=top, vtype=GRB.INTEGER, name="x")
    # The set holds at most top coins in all (not in the statement: the reference model's bound).
    model.addConstr(x.sum() <= top, name="total_coins")

    # pay[j, i] is how many coins of denomination i are used to pay amount j.
    # The bound top on pay is not in the statement: it is the reference model's bound.
    pay = model.addVars(amounts, kinds, lb=0, ub=top, vtype=GRB.INTEGER, name="pay")
    # For every amount j from 1 to top - 1, some selection of the coins in the set pays it exactly.
    model.addConstrs((gp.quicksum(denominations[i] * pay[j, i] for i in kinds) == j
                      for j in amounts), name="pays")
    # A payment uses no more coins of a kind than the set holds.
    model.addConstrs((pay[j, i] <= x[i] for j in amounts for i in kinds), name="from_set")

    # Minimise the number of coins in the set.
    model.setObjective(x.sum(), GRB.MINIMIZE)

    return model, {"x": [x[i] for i in kinds]}


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
