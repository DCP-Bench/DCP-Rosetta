# crypta: a Gurobi (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/crypta.html
# Run it (after `pip install gurobipy numpy`; the licence that comes with pip allows models
# up to 2000 variables and constraints) with:
#   python crypta.py

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Crypta: give the letters A to J distinct digits so that the addition of the two 20-letter numbers equals the 20-letter sum, with no number starting with 0."""
    # The puzzle has no instance data: the letters and the addition are fixed by the statement.
    names = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]  # the ten letters of the puzzle
    digits = range(10)  # the digits 0 to 9

    model = gp.Model("crypta")
    # Coefficients reach 10^7; tighten the integrality tolerance so the rounded digits
    # satisfy the equations exactly.
    model.Params.IntFeasTol = 1e-9

    # is_[L, v] is 1 when letter L stands for digit v.
    is_ = model.addVars(names, digits, vtype=GRB.BINARY, name="is")
    # Each letter stands for exactly one digit.
    model.addConstrs((is_.sum(L, "*") == 1 for L in names), name="one_digit")
    # No digit stands for two letters (the letters are distinct digits).
    model.addConstrs((is_.sum("*", v) <= 1 for v in digits), name="distinct")
    # value[L] is the digit of letter L, as a linear expression in is_.
    value = {L: gp.quicksum(v * is_[L, v] for v in digits) for L in names}
    A, B, C, D, E, F, G, H, I, J = (value[L] for L in names)

    # The first letter of each number (B and D of the addends, G of the sum) is not zero.
    model.addConstrs((is_[L, 0] == 0 for L in ("B", "D", "G")), name="leading")

    # Sr1 is the carry from the lowest seven columns into the middle block;
    # Sr2 is the carry from the middle block into the highest six columns.
    sr1 = model.addVar(vtype=GRB.BINARY, name="Sr1")
    sr2 = model.addVar(vtype=GRB.BINARY, name="Sr2")

    # The terms are the letters of each column, weighted by the power of ten of that column
    # (1 for the units, 10 for the tens, and so on up to 10^6).
    # The lowest seven columns add up to the lowest seven digits of the sum, carrying Sr1 out (10^7 * Sr1).
    model.addConstr(A + 10 * E + 100 * J + 1000 * B + 10000 * B + 100000 * E + 1000000 * F
                    + E + 10 * J + 100 * E + 1000 * F + 10000 * G + 100000 * A + 1000000 * F
                    == F + 10 * E + 100 * E + 1000 * H + 10000 * I + 100000 * F + 1000000 * B
                    + 10000000 * sr1, name="block1")

    # The middle seven columns add up to the middle seven digits of the sum, taking Sr1 in (the + sr1)
    # and carrying Sr2 out (10^7 * Sr2).
    model.addConstr(C + 10 * F + 100 * H + 1000 * A + 10000 * I + 100000 * I + 1000000 * J
                    + F + 10 * I + 100 * B + 1000 * D + 10000 * I + 100000 * D + 1000000 * C + sr1
                    == J + 10 * F + 100 * A + 1000 * F + 10000 * H + 100000 * D + 1000000 * D
                    + 10000000 * sr2, name="block2")

    # The highest six columns add up to the highest six digits of the sum, taking Sr2 in (the + sr2).
    model.addConstr(A + 10 * J + 100 * J + 1000 * I + 10000 * A + 100000 * B
                    + B + 10 * A + 100 * G + 1000 * F + 10000 * H + 100000 * D + sr2
                    == C + 10 * A + 100 * G + 1000 * E + 10000 * J + 100000 * G, name="block3")

    return model, value


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
