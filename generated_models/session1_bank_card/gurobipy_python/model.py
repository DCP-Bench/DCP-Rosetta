# session1_bank_card: a Gurobi (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_bank_card.html
# Run it (after `pip install gurobipy numpy`; the licence that comes with pip allows models
# up to 2000 variables and constraints) with:
#   python session1_bank_card.py

import gurobipy as gp
from gurobipy import GRB

# The four positions of the PIN, named a, b, c and d.
NAMES = "abcd"
# The digits a PIN can hold: 0 to 9.
DIGITS = range(10)


def create_model(instance):
    """Find the four-digit PIN abcd, with no two digits the same, where the two-digit number cd is three times ab and the two-digit number da is twice bc."""
    model = gp.Model("session1_bank_card")

    # is_[x, v] is 1 when the digit at position x of the PIN is v.
    is_ = model.addVars(NAMES, DIGITS, vtype=GRB.BINARY, name="is")
    # pin[x] is the digit at position x of the PIN, read back from is_.
    pin = {x: model.addVar(lb=0, ub=9, vtype=GRB.INTEGER, name=x) for x in NAMES}

    # Each position holds exactly one digit, and pin[x] is that digit.
    model.addConstrs((is_.sum(x, "*") == 1 for x in NAMES), name="one_digit")
    model.addConstrs((pin[x] == gp.quicksum(v * is_[x, v] for v in DIGITS) for x in NAMES), name="read")

    # No two digits are the same: each digit appears in at most one position.
    model.addConstrs((is_.sum("*", v) <= 1 for v in DIGITS), name="different")

    a, b, c, d = (pin[x] for x in NAMES)

    # The two-digit number cd is 3 times the two-digit number ab.
    model.addConstr(10 * c + d == 3 * (10 * a + b), name="cd_is_3_ab")

    # The two-digit number da is 2 times the two-digit number bc.
    model.addConstr(10 * d + a == 2 * (10 * b + c), name="da_is_2_bc")

    # The output is the PIN, one digit per position.
    return model, {x: pin[x] for x in NAMES}


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
