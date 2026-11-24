# best_host: a Gurobi (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/best_host.html
# Run it (after `pip install gurobipy numpy`; the licence that comes with pip allows models
# up to 2000 variables and constraints) with:
#   python best_host.py

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Seat six guests around a round table so that no two guests who do not get along sit next to each other."""
    # The puzzle has no instance data: the six guests and the two guests each one
    # will sit next to are given in the problem statement.
    n = 6
    andrew, betty, cara, dave, erica, frank = range(n)
    prefs = [
        [dave, frank],     # Andrew sits next to Dave and Frank
        [cara, erica],     # Betty sits next to Cara and Erica
        [betty, frank],    # Cara sits next to Betty and Frank
        [andrew, erica],   # Dave sits next to Andrew and Erica
        [betty, dave],     # Erica sits next to Betty and Dave
        [andrew, cara],    # Frank sits next to Andrew and Cara
    ]
    seats = range(n)
    guests = range(n)

    model = gp.Model("best_host")

    # sits[i, g] is 1 when guest g takes seat i; every seat has one guest and every
    # guest one seat (all different).
    sits = model.addVars(seats, guests, vtype=GRB.BINARY, name="sits")
    # Every seat holds exactly one guest (sits.sum(i, "*") adds over all guests).
    model.addConstrs((sits.sum(i, "*") == 1 for i in seats), name="seat")
    # Every guest sits in exactly one seat (sits.sum("*", g) adds over all seats).
    model.addConstrs((sits.sum("*", g) == 1 for g in guests), name="guest")

    # The table is round: seat i is next to seat i+1 (mod n). Two guests may be
    # neighbours only when each is on the other's list, so a pair that is not on
    # each other's list may not sit in neighbouring seats.
    model.addConstrs((sits[i, g] + sits[(i + 1) % n, h] <= 1
                      for i in seats for g in guests for h in guests
                      if g != h and not (h in prefs[g] and g in prefs[h])), name="conflict")

    # x[i]: the guest on seat i (Andrew 0 .. Frank 5).
    return model, {"x": [gp.quicksum(g * sits[i, g] for g in guests) for i in seats]}


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
