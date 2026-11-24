# birthday_coins: a Gurobi (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/birthday_coins.html
# Run it (after `pip install gurobipy numpy`; the licence that comes with pip allows models
# up to 2000 variables and constraints) with:
#   python birthday_coins.py

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Tommy's 15 birthday coins (half-crowns, shillings and sixpences) add up to 1 pound 5 shillings 6 pence: how many of them are half-crowns?"""
    # The puzzle has no instance data: the coins and the total are fixed by the statement.
    values = [30, 12, 6]              # in pence: a half-crown (2 shillings 6 pence), a shilling, a sixpence
    total_value = 240 + 5 * 12 + 6    # 1 pound 5 shillings 6 pence, in pence (a pound is 240 pence)
    total_coins = 15                  # the number of coins Tommy was given

    model = gp.Model("birthday_coins")

    # coins[i] is how many coins of kind i Tommy was given: kind 0 is a half-crown, 1 a shilling, 2 a sixpence.
    # Each kind is at most all 15 coins, which the count constraint implies anyway.
    coins = model.addVars(len(values), lb=0, ub=total_coins, vtype=GRB.INTEGER, name="coins")

    # The coins are worth 1 pound 5 shillings 6 pence.
    model.addConstr(gp.quicksum(v * coins[i] for i, v in enumerate(values)) == total_value, name="value")

    # He was given 15 coins.
    model.addConstr(coins.sum() == total_coins, name="count")

    # No objective: any count of coins that meets both constraints answers the puzzle.
    return model, {"half_crowns": coins[0]}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.Params.OutputFlag = 0  # no solver log
    model.optimize()

    if model.Status == GRB.OPTIMAL:  # a solution
        # a variable's value is var.X, an expression's is expr.getValue(); both read through LinExpr
        value = np.vectorize(lambda out: round(gp.LinExpr(out).getValue()))
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution, Gurobi status", model.Status)  # 3 infeasible, 4 infeasible or unbounded
