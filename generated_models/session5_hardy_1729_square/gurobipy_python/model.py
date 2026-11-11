# session5_hardy_1729_square: a Gurobi (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_hardy_1729_square.html
# Run it (after `pip install gurobipy numpy`; the licence that comes with pip allows models
# up to 2000 variables and constraints) with:
#   python session5_hardy_1729_square.py

import gurobipy as gp
from gurobipy import GRB


# The problem has no instance data: the numbers lie between 1 and 100, as the statement says.
RANGE_MIN, RANGE_MAX = 1, 100
NAMES = "abcd"  # the four numbers a, b, c, d (the output names)


def create_model(instance):
    """Hardy's 1729 square: find four different whole numbers from 1 to 100, a, b, c and d, with a^2 + b^2 = c^2 + d^2."""
    model = gp.Model("session5_hardy_1729_square")
    # Squares reach 10,000, so a tight integrality tolerance keeps a binary that is near 0 or 1
    # from shifting a square.
    model.Params.IntFeasTol = 1e-9

    values = range(RANGE_MIN, RANGE_MAX + 1)

    # is_[x, v] is 1 when number x equals v. Each number and its square are linear in these
    # binaries, so no product of two variables is needed.
    is_ = model.addVars(NAMES, values, vtype=GRB.BINARY, name="is")
    number, square = {}, {}
    for x in NAMES:
        # Each number takes exactly one value.
        model.addConstr(is_.sum(x, "*") == 1, name=f"one_value[{x}]")
        # number[x] is the number x itself, an integer from 1 to 100.
        number[x] = model.addVar(lb=RANGE_MIN, ub=RANGE_MAX, vtype=GRB.INTEGER, name=x)
        model.addConstr(number[x] == gp.quicksum(v * is_[x, v] for v in values), name=f"read[{x}]")
        # square[x] is the square of x, as a linear expression over the binaries.
        square[x] = gp.quicksum(v * v * is_[x, v] for v in values)

    # The four numbers are all different: each value is taken by at most one of them.
    model.addConstrs((is_.sum("*", v) <= 1 for v in values), name="different")

    # The sum of squares: a^2 + b^2 = c^2 + d^2.
    model.addConstr(square["a"] + square["b"] == square["c"] + square["d"], name="sum_of_squares")

    # No objective: any four numbers that meet the rules are a solution.
    return model, {x: number[x] for x in NAMES}


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
