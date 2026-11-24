# eighteen_hole_golf: a Gurobi (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/eighteen_hole_golf.html
# Run it (after `pip install gurobipy numpy`; the licence that comes with pip allows models
# up to 2000 variables and constraints) with:
#   python eighteen_hole_golf.py

import gurobipy as gp
from gurobipy import GRB

# The problem has no instance data: 18 holes, lengths 3..5, total 72, as stated.
NUM_HOLES = 18            # the number of holes on the course (from the statement)
TOTAL_LENGTH = 72         # the total length of the course (from the statement)
SHORTEST, LONGEST = 3, 5  # the length of each hole is 3, 4 or 5 (from the statement)


def create_model(instance):
    """Eighteen-hole golf: give each of 18 holes a length of 3, 4 or 5 so that the course totals 72."""
    model = gp.Model("eighteen_hole_golf")

    # holes[i] is the length of hole i, which is 3, 4 or 5.
    holes = model.addVars(NUM_HOLES, lb=SHORTEST, ub=LONGEST, vtype=GRB.INTEGER, name="hole")

    # The lengths of the holes add up to the total length of the course.
    model.addConstr(holes.sum() == TOTAL_LENGTH, name="total_length")

    return model, {"holes": list(holes.values())}


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
