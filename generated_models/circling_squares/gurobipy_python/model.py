# circling_squares: a Gurobi (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/circling_squares.html
# Run it (after `pip install gurobipy numpy`; the licence that comes with pip allows models
# up to 2000 variables and constraints) with:
#   python circling_squares.py

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Circling the squares: ten different numbers in a circle where the squares of any two
    adjacent numbers sum to the same as the squares of the two numbers diametrically opposite."""
    # The puzzle has no instance data. The circle and the four given numbers are the puzzle's own.
    names = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "K"]  # the ten squares in circle order (there is no J)
    given = {"A": 16, "B": 2, "F": 8, "G": 14}                   # the four numbers that stand as they are
    # 1..99: the upper bound is from the statement (no number needs more than two figures);
    # the lower bound 1 is not in the statement and keeps the numbers positive.
    values = range(1, 100)

    model = gp.Model("circling_squares")
    # Squares reach 99^2 = 9801; tighten the integrality tolerance so a binary cannot
    # carry a fraction of such a coefficient.
    model.Params.IntFeasTol = 1e-9

    # is_[p, v] is 1 when square p holds the number v; this makes the squares linear.
    is_ = model.addVars(names, values, vtype=GRB.BINARY, name="is")
    # Each square holds exactly one number.
    model.addConstrs((is_.sum(p, "*") == 1 for p in names), name="one_number")
    # number[p] is the number in square p, and square[p] its square.
    number = {p: gp.quicksum(v * is_[p, v] for v in values) for p in names}
    square = {p: gp.quicksum(v * v * is_[p, v] for v in values) for p in names}

    # Every square holds a different number: each value is used at most once.
    model.addConstrs((is_.sum("*", v) <= 1 for v in values), name="different")

    # The four example numbers stand as they are: A = 16, B = 2, F = 8, G = 14.
    model.addConstrs((is_[p, v] == 1 for p, v in given.items()), name="given")

    # Each pair of adjacent squares has the same sum of squares as the diametrically opposite
    # pair: A,B with F,G; B,C with G,H; C,D with H,I; D,E with I,K; E,F with K,A.
    model.addConstrs((square[p] + square[q] == square[r] + square[s]
                      for (p, q, r, s) in [("A", "B", "F", "G"), ("B", "C", "G", "H"),
                                           ("C", "D", "H", "I"), ("D", "E", "I", "K"),
                                           ("E", "F", "K", "A")]), name="opposite")

    return model, number


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
