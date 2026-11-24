# hanging_weights: a Gurobi (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/hanging_weights.html
# Run it (after `pip install gurobipy numpy`; the licence that comes with pip allows models
# up to 2000 variables and constraints) with:
#   python hanging_weights.py

import gurobipy as gp
from gurobipy import GRB

# The problem has no instance data: the thirteen weights A to M (NAMES), the values 1 to 13
# each weight can take (VALUES, from the statement), and the balance equations of the drawn mobile.
NAMES = "abcdefghijklm"
VALUES = range(1, 14)


def create_model(instance):
    """Hanging weights: give each weight A to M a whole value from 1 to 13 so that every bar of the mobile balances."""
    model = gp.Model("hanging_weights")

    # w[name] is the value of weight name, a whole number from 1 to 13.
    w = {name: model.addVar(lb=VALUES[0], ub=VALUES[-1], vtype=GRB.INTEGER, name=name) for name in NAMES}
    a, b, c, d, e, f, g, h, i, j, k, l, m = (w[name] for name in NAMES)

    # Each bar balances: the weights on one side, each times its distance from the pivot, add up to the
    # same as on the other side. A bar hanging beneath another counts as its total weight.
    model.addConstr(4 * a == b, name="bar_ab")  # bottom left: 4*A = B
    model.addConstr(5 * c == d, name="bar_cd")  # bottom right: 5*C = D (given in the statement)
    model.addConstr(3 * e == 2 * f, name="bar_ef")  # the bar of E and F: 3*E = 2*F
    model.addConstr(3 * g == 2 * (c + d), name="bar_g_cd")  # the bar of G, under the C-D bar: 3*G = 2*(C+D) (given in the statement)
    model.addConstr(3 * (a + b) + 2 * j == k + 2 * (g + c + d), name="bar_j_k")  # the bar of J and K: 3*(A+B) + 2*J = K + 2*(G+C+D)
    model.addConstr(3 * h == 2 * (e + f) + 3 * i, name="bar_h_i")  # the bar of H and I: 3*H = 2*(E+F) + 3*I
    model.addConstr(h + i + e + f == l + 4 * m, name="bar_l_m")  # the bar of L and M: H+I+E+F = L + 4*M
    model.addConstr(4 * (l + m + h + i + e + f) == 3 * (j + k + g + a + b + c + d), name="top_bar")  # the top bar: 4*(L+M+H+I+E+F) = 3*(J+K+G+A+B+C+D)

    # No objective: the puzzle only asks for weights that balance.
    return model, {n: w[n] for n in NAMES}


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
