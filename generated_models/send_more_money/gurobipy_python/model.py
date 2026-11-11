# send_more_money: a Gurobi (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/send_more_money.html
# Run it (after `pip install gurobipy numpy`; the licence that comes with pip allows models
# up to 2000 variables and constraints) with:
#   python send_more_money.py

import gurobipy as gp
from gurobipy import GRB

# The letters of the puzzle, from the statement: SEND + MORE = MONEY.
LETTERS = "sendmory"
# The digits a letter can stand for, from the statement: 0 to 9.
DIGITS = range(10)


def create_model(instance):
    """SEND + MORE = MONEY: give each letter a different digit so that the two words add up to the third, with the first letter of each word not zero."""
    model = gp.Model("send_more_money")

    # stands[L, d] is 1 when letter L stands for digit d.
    stands = model.addVars(LETTERS, DIGITS, vtype=GRB.BINARY, name="stands")
    # digit[L] is the digit of letter L, from 0 to 9.
    digit = model.addVars(LETTERS, lb=0, ub=9, vtype=GRB.INTEGER, name="digit")

    # Each letter stands for exactly one digit (stands.sum(L, "*") adds over all digits d).
    model.addConstrs((stands.sum(L, "*") == 1 for L in LETTERS), name="one_digit")
    # digit[L] is the digit that letter L stands for.
    model.addConstrs((digit[L] == gp.quicksum(d * stands[L, d] for d in DIGITS) for L in LETTERS), name="read")

    # Different letters stand for different digits: each digit is used by at most one letter.
    model.addConstrs((stands.sum("*", d) <= 1 for d in DIGITS), name="different")

    # The number a word spells: its letters' digits, each weighted by its place value.
    def word(w):
        return gp.quicksum(10 ** (len(w) - 1 - k) * digit[ch] for k, ch in enumerate(w))

    # SEND + MORE = MONEY.
    model.addConstr(word("send") + word("more") == word("money"), name="sum")

    # The first letter of SEND and of MORE is not zero (MONEY starts with M too).
    model.addConstrs((digit[L] >= 1 for L in "sm"), name="leading")

    # No objective: any assignment that meets the rules will do.
    return model, {L: digit[L] for L in LETTERS}


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
