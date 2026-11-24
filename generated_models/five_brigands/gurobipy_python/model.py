# five_brigands: a Gurobi (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/five_brigands.html
# Run it (after `pip install gurobipy numpy`; the licence that comes with pip allows models
# up to 2000 variables and constraints) with:
#   python five_brigands.py

import gurobipy as gp
from gurobipy import GRB

# The problem has no instance data: 200 doubloons and the multipliers
# 12, 3, 1, 1/2 and 1/3 come from the statement.
TOTAL = 200


def create_model(instance):
    """Five brigands together have exactly 200 doubloons, and each has at least one. Find how many each has, given that the same 200 would result if their shares were multiplied as the statement says."""
    model = gp.Model("five_brigands")

    # Doubloons of Alfonso (A), Benito (B), Carlos (C), Diego (D) and Esteban (E).
    # Each has at least 1, as the statement says. The upper bound TOTAL is not in the
    # statement: it only keeps the variables finite, and follows from the total and the lower bounds.
    A, B, C, D, E = (model.addVar(lb=1, ub=TOTAL, vtype=GRB.INTEGER, name=name) for name in "ABCDE")

    # Altogether they have exactly 200 doubloons.
    model.addConstr(A + B + C + D + E == TOTAL, name="total")

    # If Alfonso had 12 times as much, Benito 3 times, Carlos the same, Diego half and
    # Esteban a third, the total would still be 200. The equation is multiplied by 6
    # to clear the fractions.
    model.addConstr(6 * (12 * A + 3 * B + C) + 3 * D + 2 * E == 6 * TOTAL, name="scaled_total")

    return model, {"A": A, "B": B, "C": C, "D": D, "E": E}


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
