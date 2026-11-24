# chess_set: a Gurobi (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/chess_set.html
# Run it (after `pip install gurobipy numpy`; the licence that comes with pip allows models
# up to 2000 variables and constraints) with:
#   python chess_set.py

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Chess sets: how many small and large boxwood chess sets to make each week to maximise profit under lathe-hour and boxwood limits."""
    # The problem has no instance data: the hours, kilograms, limits and profits are the
    # statement's own.
    model = gp.Model("chess_set")

    # small_set and large_set: the number of small and large sets made each week
    # (the lathe-hour and boxwood limits keep them finite)
    small_set = model.addVar(lb=0, vtype=GRB.INTEGER, name="small_set")
    large_set = model.addVar(lb=0, vtype=GRB.INTEGER, name="large_set")

    # Boxwood: a small set uses 1 kg and a large set 3 kg, and only 200 kg a week can be obtained.
    model.addConstr(small_set + 3 * large_set <= 200, name="boxwood")

    # Lathe hours: a small set takes 3 hours and a large set 2 hours; four lathes of 40 hours a week give 160 hours.
    model.addConstr(3 * small_set + 2 * large_set <= 160, name="lathe")

    # max_profit: the profit of the week in dollars, $5 for each small set and $20 for each large set
    max_profit = 5 * small_set + 20 * large_set

    # Objective: maximise the profit.
    model.setObjective(max_profit, GRB.MAXIMIZE)

    return model, {"small_set": small_set, "large_set": large_set, "max_profit": max_profit}


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
