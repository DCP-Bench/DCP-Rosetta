# added_corners: a Gurobi (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/added_corners.html
# Run it (after `pip install gurobipy numpy`; the licence that comes with pip allows models
# up to 2000 variables and constraints) with:
#   python added_corners.py

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Added corners: enter the digits 1 to 8 in the circles and squares of the figure so that each square is the sum of the two circles next to it."""
    # The puzzle has no instance data: the layout is the picture in the statement,
    #   a b c    C F C    circles (C) are a, c, f, h; squares (F) are b, d, e, g.
    #   d   e    F   F
    #   f g h    C F C
    n = 8
    places = range(n)  # the eight positions a to h, read left to right, top to bottom
    digits = range(1, n + 1)  # the digits 1 to 8, from the statement

    model = gp.Model("added_corners")

    # put[p, v] is 1 when position p holds digit v, and 0 when not.
    put = model.addVars(places, digits, vtype=GRB.BINARY, name="put")
    # positions[p] is the digit at position p, read back from put.
    positions = [gp.quicksum(v * put[p, v] for v in digits) for p in places]
    a, b, c, d, e, f, g, h = positions

    # Every position holds exactly one digit.
    model.addConstrs((put.sum(p, "*") == 1 for p in places), name="one_digit")
    # Each digit is used exactly once: the digits are all different.
    model.addConstrs((put.sum("*", v) == 1 for v in digits), name="used_once")

    # Each square is the sum of the two circles next to it.
    model.addConstr(b == a + c, name="top")  # square b: circles a and c
    model.addConstr(d == a + f, name="left")  # square d: circles a and f
    model.addConstr(e == c + h, name="right")  # square e: circles c and h
    model.addConstr(g == f + h, name="bottom")  # square g: circles f and h

    # No objective: the puzzle only asks for an arrangement that obeys the rules.
    return model, {"positions": positions}


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
