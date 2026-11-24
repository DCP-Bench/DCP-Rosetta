# age_changing: a Gurobi (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/age_changing.html
# Run it (after `pip install gurobipy numpy`; the licence that comes with pip allows models
# up to 2000 variables and constraints) with:
#   python age_changing.py

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Age changing: applying +2, /8, -3 and *7 in some order to my age gives my husband's age,
    and applying the same four operations in a different order to his age gives mine."""
    # The puzzle has no instance data. The age range 16..120 and the range 1..1000 of
    # intermediate values are not in the statement: they are bounds taken from the reference,
    # chosen to keep the variables finite.
    n_ops = 4                    # the four operations: 0: +2, 1: /8, 2: -3, 3: *7
    age_low, age_high = 16, 120  # ages; not in the statement (bound from the reference)
    steps = range(n_ops)
    ops = range(n_ops)

    model = gp.Model("age_changing")

    m = model.addVar(lb=age_low, ub=age_high, vtype=GRB.INTEGER, name="m")   # my age
    h = model.addVar(lb=age_low, ub=age_high, vtype=GRB.INTEGER, name="h")   # husband's age

    # hlist[i] is the value after i operations of the first sequence, which starts at my
    # age; mlist[i] is the value after i operations of the second, which starts at his age.
    hlist = model.addVars(n_ops + 1, lb=1, ub=1000, vtype=GRB.INTEGER, name="hlist")  # 1..1000: not in the statement
    mlist = model.addVars(n_ops + 1, lb=1, ub=1000, vtype=GRB.INTEGER, name="mlist")  # 1..1000: not in the statement
    # The first sequence ends at his age, and the second ends at mine.
    model.addConstr(hlist[0] == m)
    model.addConstr(hlist[n_ops] == h)
    model.addConstr(mlist[0] == h)
    model.addConstr(mlist[n_ops] == m)

    # order1[i, o] (order2[i, o]) is 1 when operation o is applied at step i of the
    # first (second) sequence.
    order1 = model.addVars(steps, ops, vtype=GRB.BINARY, name="order1")
    order2 = model.addVars(steps, ops, vtype=GRB.BINARY, name="order2")
    for order in (order1, order2):
        # Each step applies exactly one operation.
        model.addConstrs((order.sum(i, "*") == 1 for i in steps))
        # Each of the four operations is applied exactly once.
        model.addConstrs((order.sum("*", o) == 1 for o in ops))

    # The two sequences use the same operations in a different order, so they agree on at
    # most n_ops - 1 steps. same[i, o] is at least 1 when both sequences apply o at step i.
    same = model.addVars(steps, ops, vtype=GRB.BINARY, name="same")
    model.addConstrs((same[i, o] >= order1[i, o] + order2[i, o] - 1 for i in steps for o in ops))
    model.addConstr(same.sum() <= n_ops - 1, name="different_order")

    # Each step applies its operation to the previous value. The statement does not say that
    # dividing by 8 must be exact; the reference writes it as 8 * new == old, which is kept.
    for order, values in ((order1, hlist), (order2, mlist)):
        for i in steps:
            old, new = values[i], values[i + 1]
            model.addConstr((order[i, 0] == 1) >> (new == old + 2))   # +2
            model.addConstr((order[i, 1] == 1) >> (8 * new == old))   # /8, exact as in the reference
            model.addConstr((order[i, 2] == 1) >> (new == old - 3))   # -3
            model.addConstr((order[i, 3] == 1) >> (new == 7 * old))   # *7

    return model, {"m": m, "h": h}


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
