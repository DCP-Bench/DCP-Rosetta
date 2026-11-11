# bananas: a Gurobi (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bananas.html
# Run it (after `pip install gurobipy numpy`; the licence that comes with pip allows models
# up to 2000 variables and constraints) with:
#   python bananas.py

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Buy 100 fruits for exactly 100 dollars, buying at least one of each kind, with as few bananas and apples as possible."""
    # The puzzle has no instance data: the prices and totals are the puzzle's own.
    model = gp.Model("bananas")

    # The number of each kind bought: at least 1 of each, since every kind must be bought.
    # The upper bound of 100 is not in the statement: it follows from buying 100 fruits in all.
    bananas = model.addVar(lb=1, ub=100, vtype=GRB.INTEGER, name="bananas")
    oranges = model.addVar(lb=1, ub=100, vtype=GRB.INTEGER, name="oranges")
    mangoes = model.addVar(lb=1, ub=100, vtype=GRB.INTEGER, name="mangoes")
    apples = model.addVar(lb=1, ub=100, vtype=GRB.INTEGER, name="apples")

    # The 100 dollars are spent exactly. Prices: 5 bananas for 3 dollars (3/5 each), 7 oranges
    # for 5 dollars (5/7 each), 9 mangoes for 7 dollars (7/9 each), 3 apples for 9 dollars (9/3 each).
    # Both sides are multiplied by 3*5*7*9 = 945 so that the coefficients are whole numbers.
    model.addConstr(3 * 189 * bananas + 5 * 135 * oranges + 7 * 105 * mangoes + 9 * 315 * apples == 100 * 945,
                    name="dollars")

    # 100 fruits in total.
    model.addConstr(bananas + oranges + mangoes + apples == 100, name="fruits")

    # Objective: buy as few bananas and apples as possible, as the buyer does not like them.
    model.setObjective(bananas + apples, GRB.MINIMIZE)

    return model, {"bananas": bananas, "oranges": oranges, "mangoes": mangoes, "apples": apples}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
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
