# general_store: a Gurobi (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/general_store.html
# Run it (after `pip install gurobipy numpy`; the licence that comes with pip allows models
# up to 2000 variables and constraints) with:
#   python general_store.py

import gurobipy as gp
from gurobipy import GRB

# The sixteen words added up on the sign, spaces removed, in the order of the statement (the problem has no instance data).
ADDENDS = ["CHESS", "CASH", "BOWWOW", "CHOPS", "ALSOPS", "PALEALE", "COOL", "BASS",
           "HOPS", "ALES", "HOES", "APPLES", "COWS", "CHEESE", "CHSOAP", "SHEEP"]
# The total the addends must make: ALL WOOL, from the statement.
TOTAL = "ALLWOOL"
# The ten different letters of the puzzle, each standing for a different digit.
LETTERS = "CHESABOWPL"
# The digits 0 to 9.
DIGITS = range(10)


def create_model(instance):
    """General store: find a digit for each letter, different letters standing for different digits, so that the sixteen words on the sign add up to ALL WOOL."""
    model = gp.Model("general_store")

    # is_[L, d] is 1 when letter L stands for digit d, and 0 when not.
    is_ = model.addVars(LETTERS, DIGITS, vtype=GRB.BINARY, name="is")
    # digit[L] is the digit that letter L stands for, read back from is_ (the bounds 0 and 9 are the digits).
    digit = {L: model.addVar(lb=0, ub=9, vtype=GRB.INTEGER, name=L) for L in LETTERS}

    # Each letter stands for exactly one digit.
    model.addConstrs((is_.sum(L, "*") == 1 for L in LETTERS), name="one_digit")
    # The digit of each letter is the d whose is_[L, d] is 1.
    model.addConstrs((digit[L] == gp.quicksum(d * is_[L, d] for d in DIGITS) for L in LETTERS), name="read")

    # Different letters stand for different digits: each digit is used by at most one letter.
    model.addConstrs((is_.sum("*", d) <= 1 for d in DIGITS), name="different")

    # The sixteen words add up to ALL WOOL. The addition is posted column by column from the units column, with carries as done by hand: one equation over the whole words has place values up to 10^6, so a small integrality tolerance on one digit would move the sum by about 10.
    width = max(len(TOTAL), max(len(w) for w in ADDENDS))  # the number of columns, from the units column
    # Not from the statement: a bound on the carries, large enough for sixteen addends of up to nine in a column.
    max_carry = (len(ADDENDS) * 9 + len(ADDENDS)) // 10
    # carry[c] is the amount carried into column c from the column to its right (column 0 is the units column).
    carry = [model.addVar(lb=0, ub=max_carry, vtype=GRB.INTEGER, name=f"carry[{c}]") for c in range(width + 1)]
    # No carry comes into the units column, and none goes out of the leftmost column.
    model.addConstr(carry[0] == 0, name="no_carry_into_units")
    model.addConstr(carry[width] == 0, name="no_carry_out")
    # Column c: the digits of the addends in that column, plus the carry in, equal the digit of ALL WOOL in that column, plus ten times the carry out.
    model.addConstrs((
        gp.quicksum(digit[w[-1 - c]] for w in ADDENDS if c < len(w)) + carry[c]
        == (digit[TOTAL[-1 - c]] if c < len(TOTAL) else 0) + 10 * carry[c + 1]
        for c in range(width)), name="column")

    # There is no objective: any digits that satisfy the sum are a solution. The output is the digit of each letter.
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
