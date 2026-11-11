# giant_cat_army: a Gurobi (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/giant_cat_army.html
# Run it (after `pip install gurobipy numpy`; the licence that comes with pip allows models
# up to 2000 variables and constraints) with:
#   python giant_cat_army.py

import math

import gurobipy as gp
from gurobipy import GRB

# Constants from the statement: the numbers are whole numbers of at most 60, the list
# has 24 numbers, it starts at 0 and ends at 14, and 2 and 10 must both appear, 2 first.
MAXVAL = 60
N = 24
START, END = 0, 14
FIRST, SECOND = 2, 10  # 2 and 10 must appear, 2 before 10
STEPS = (5, 7)         # the two additions allowed


def create_model(instance):
    """Giant cat army: starting from 0, build a list of 24 distinct whole numbers, each at most 60, by adding 5, adding 7 or taking a square root, so that the list ends with 14 and 2, 10 and 14 appear in that order."""
    model = gp.Model("giant_cat_army")

    # x[i] is the i-th number in the list, counting from 0: a whole number from 0 to 60.
    x = model.addVars(N, lb=0, ub=MAXVAL, vtype=GRB.INTEGER, name="x")

    # The list starts with 0 and ends with 14.
    model.addConstr(x[0] == START, name="start")
    model.addConstr(x[N - 1] == END, name="end")

    # The second number is 5 or 7. Not stated in the statement: it follows from the
    # distinctness rule, because taking the root of 0 would repeat 0.
    second_is_5 = model.addVar(vtype=GRB.BINARY, name="second_is_5")  # 1 when the second number is 5
    model.addConstr(x[1] == 7 - 2 * second_is_5, name="second_number")

    # Each step from x[i] to x[i+1] is exactly one operation: add 5, add 7, or take the square root.
    # root[r] is 1 when the root taken is r, so that x[i] = r*r and x[i+1] = r; r*r is at most 60.
    roots = range(math.isqrt(MAXVAL) + 1)
    for i in range(N - 1):
        add = {s: model.addVar(vtype=GRB.BINARY, name=f"add{s}[{i}]") for s in STEPS}  # add[s] is 1 when the step adds s
        sqrt = model.addVar(vtype=GRB.BINARY, name=f"sqrt[{i}]")                      # 1 when the step takes a square root
        model.addConstr(gp.quicksum(add.values()) + sqrt == 1, name=f"one_operation[{i}]")
        for s, b in add.items():
            model.addConstr((b == 1) >> (x[i + 1] == x[i] + s), name=f"add{s}_step[{i}]")
        root = model.addVars(roots, vtype=GRB.BINARY, name=f"root[{i}]")
        model.addConstr(root.sum() == sqrt, name=f"root_chosen[{i}]")
        model.addConstr((sqrt == 1) >> (x[i] == gp.quicksum(r * r * root[r] for r in roots)), name=f"square[{i}]")
        model.addConstr((sqrt == 1) >> (x[i + 1] == gp.quicksum(r * root[r] for r in roots)), name=f"root_step[{i}]")

    # The numbers are distinct: for each pair of positions i < j, x[i] is below x[j] or above it.
    # below[i, j] is 1 when x[i] is below x[j].
    pairs = [(i, j) for i in range(N) for j in range(i + 1, N)]
    below = model.addVars(pairs, vtype=GRB.BINARY, name="below")
    model.addConstrs(((below[i, j] == 1) >> (x[i] <= x[j] - 1) for i, j in pairs), name="below_if")
    model.addConstrs(((below[i, j] == 0) >> (x[i] >= x[j] + 1) for i, j in pairs), name="above_if")

    # 2 and 10 must appear in the list, each exactly once (distinctness), at a position from
    # 1 to N-1, since position 0 holds 0. The helper returns the position of the value.
    def appears(value, name):
        where = model.addVars(range(1, N), vtype=GRB.BINARY, name=name)  # where[i] is 1 when the value is at position i
        model.addConstr(where.sum() == 1, name=f"{name}_once")
        model.addConstrs(((where[i] == 1) >> (x[i] == value) for i in range(1, N)), name=f"{name}_at")
        return gp.quicksum(i * where[i] for i in range(1, N))

    # 2 appears before 10: the position of 2 is less than the position of 10.
    model.addConstr(appears(FIRST, "pos2") <= appears(SECOND, "pos10") - 1, name="order")

    # No objective: any list that meets the rules will do.
    return model, {"x": [x[i] for i in range(N)]}


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
