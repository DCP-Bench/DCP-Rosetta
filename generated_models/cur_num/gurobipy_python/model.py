# cur_num: a Gurobi (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cur_num.html
# Run it (after `pip install gurobipy numpy`; the licence that comes with pip allows models
# up to 2000 variables and constraints) with:
#   python cur_num.py

import gurobipy as gp
from gurobipy import GRB

# The statement asks for a number between 1 and 10000.
UPPER = 10000
# The example in the statement, which the answer must not be: 48 + 1 = 49 = 7 * 7, and 48 / 2 + 1 = 25 = 5 * 5.
KNOWN = 48


def create_model(instance):
    """Curious numbers: find a number between 1 and 10000, other than 48, such that adding 1 to it gives a square, and adding 1 to half of it also gives a square."""
    model = gp.Model("cur_num")

    # The square roots of the squares up to 10000 lie in 1..100; that range is not in the statement,
    # it is chosen to cover them. root_b[v] is 1 when the number plus 1 is v * v, and root_e[v] is 1
    # when half the number plus 1 is v * v. Exactly one root of each is chosen.
    roots = range(1, int(UPPER ** 0.5) + 1)
    root_b = model.addVars(roots, vtype=GRB.BINARY, name="b")
    root_e = model.addVars(roots, vtype=GRB.BINARY, name="e")
    model.addConstr(root_b.sum() == 1, name="one_b")
    model.addConstr(root_e.sum() == 1, name="one_e")

    # The number, peculiar, plus 1 is b * b, so peculiar = b * b - 1. The number is at least 1, the
    # lower end of the statement's range; the upper end holds because b is at most 100.
    peculiar = gp.quicksum((v * v - 1) * root_b[v] for v in roots)
    model.addConstr(peculiar >= 1, name="peculiar_at_least_1")

    # Half the number, half, plus 1 is e * e, so half = e * e - 1; the number is twice its half.
    half = gp.quicksum((v * v - 1) * root_e[v] for v in roots)
    model.addConstr(peculiar == 2 * half, name="halving")

    # Redundant, not in the statement: it adds nothing, since the constraints above already give half >= 1.
    model.addConstr(half >= 1, name="half_at_least_1")

    # The answer is another number, not 48: its root b may not be 7, the root that gives 48.
    for v in roots:
        if v * v - 1 == KNOWN:
            model.addConstr(root_b[v] == 0, name="not_48")

    # peculiar is the number found.
    return model, {"peculiar": peculiar}


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
