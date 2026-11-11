# pythagorean_triplet: a Gurobi (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/pythagorean_triplet.html
# Run it (after `pip install gurobipy numpy`; the licence that comes with pip allows models
# up to 2000 variables and constraints) with:
#   python pythagorean_triplet.py

import gurobipy as gp
from gurobipy import GRB

# The statement says the three numbers sum to 1000.
TOTAL = 1000
# Not in the statement: each number is at most 500. a + b > c (as in any triangle), so with
# a + b + c = 1000 the largest number c is below 500, and so are the others; the bound cuts off no solution.
UPPER = 500


def create_model(instance):
    """Pythagorean triplet: three whole numbers a, b, c with a^2 + b^2 = c^2 and a + b + c = 1000."""
    model = gp.Model("pythagorean_triplet")

    # The three numbers a, b, c.
    a, b, c = (model.addVar(lb=1, ub=UPPER, vtype=GRB.INTEGER, name=v) for v in "abc")

    # The statement orders the numbers: a < b < c.
    model.addConstr(a + 1 <= b, name="a_below_b")
    model.addConstr(b + 1 <= c, name="b_below_c")

    # The three numbers sum to 1000.
    model.addConstr(a + b + c == TOTAL, name="sum")

    # Pythagoras: a^2 + b^2 = c^2 (a quadratic constraint, which Gurobi handles directly).
    model.addConstr(a * a + b * b == c * c, name="pythagoras")

    # No objective: any assignment satisfying the constraints is a solution.

    return model, {"a": a, "b": b, "c": c}


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
