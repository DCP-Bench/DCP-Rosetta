# fancy_dress: a Gurobi (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fancy_dress.html
# Run it (after `pip install gurobipy numpy`; the licence that comes with pip allows models
# up to 2000 variables and constraints) with:
#   python fancy_dress.py

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Choose the green items Mr Greenguest wears, or pay the entrance fee, at the least cost, so that he meets the dress rules and may join the party."""
    model = gp.Model("fancy_dress")

    # t: 1 when he wears a green tie, 0 when not
    # h: 1 when he wears a green hat, 0 when not
    # r: 1 when he wears a green shirt, 0 when not; he owns one, so it is not in the cost
    # s: 1 when he wears green socks, 0 when not
    # n: 1 when he pays the entrance fee instead of following the rules, 0 when not
    t = model.addVar(vtype=GRB.BINARY, name="t")
    h = model.addVar(vtype=GRB.BINARY, name="h")
    r = model.addVar(vtype=GRB.BINARY, name="r")
    s = model.addVar(vtype=GRB.BINARY, name="s")
    n = model.addVar(vtype=GRB.BINARY, name="n")

    # Each rule is written as a clause: "a or b or not c" becomes a + b + (1 - c) >= 1.
    # Paying the fee (n) is the alternative to the rules, so n appears in every constraint.

    # Rule 1: a guest wearing a green tie has to wear a green shirt.
    model.addConstr((1 - t) + r + n >= 1, name="rule1")

    # Rule 2: green socks, or a green shirt, need a green tie or a green hat.
    model.addConstr((1 - s) + t + h + n >= 1, name="rule2_socks")
    model.addConstr((1 - r) + t + h + n >= 1, name="rule2_shirt")

    # Rule 3: a green shirt, a green hat, or no green socks needs a green tie.
    model.addConstr((1 - r) + t + n >= 1, name="rule3_shirt")
    model.addConstr((1 - h) + t + n >= 1, name="rule3_hat")
    model.addConstr(s + t + n >= 1, name="rule3_no_socks")

    # What he pays, from the statement: tie $10, hat $2, socks $12, entrance fee $11.
    model.setObjective(10 * t + 2 * h + 12 * s + 11 * n, GRB.MINIMIZE)

    return model, {"t": t, "h": h, "r": r, "s": s, "n": n}


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
