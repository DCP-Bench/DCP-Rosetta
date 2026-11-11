# csplib_009_perfect_square_placement: a Gurobi (Python) model from DCP Rosetta.
# Download the `csplib_009_perfect_square_placement.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_009_perfect_square_placement.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python csplib_009_perfect_square_placement.py csplib_009_perfect_square_placement.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Perfect square placement: pack squares of the given sides, without overlap, into a larger square so that they cover it exactly."""
    base = instance["base"]    # the side of the big square
    sides = instance["sides"]  # sides[i]: the side of small square i
    # The areas of the small squares add up to base * base (given by the statement), so squares that
    # do not overlap cover the big square exactly; no covering constraint is needed.
    squares = range(len(sides))

    model = gp.Model("csplib_009_perfect_square_placement")

    # x[i] and y[i] are the coordinates of the lower-left corner of square i, counting from 0.
    # Each square lies inside the big square, so its corner is at most base - sides[i] in each direction.
    x = model.addVars(squares, lb=0, ub=[base - s for s in sides], vtype=GRB.INTEGER, name="x")
    y = model.addVars(squares, lb=0, ub=[base - s for s in sides], vtype=GRB.INTEGER, name="y")

    # Each pair of squares a < b lies apart: one of four binaries says which side of the other it is on.
    pairs = [(a, b) for a in squares for b in squares if a < b]
    # left_of[a, b] is 1 when square a is entirely left of square b; right_of, below and above likewise.
    left_of = model.addVars(pairs, vtype=GRB.BINARY, name="left_of")
    right_of = model.addVars(pairs, vtype=GRB.BINARY, name="right_of")
    below = model.addVars(pairs, vtype=GRB.BINARY, name="below")
    above = model.addVars(pairs, vtype=GRB.BINARY, name="above")

    # Each placement is written with a big-M of base: when its binary is 0 the constraint always holds,
    # because the left side x[a] + sides[a] is at most base and x[b] is at least 0.
    model.addConstrs((x[a] + sides[a] <= x[b] + base * (1 - left_of[a, b]) for a, b in pairs), name="left_of_rule")
    model.addConstrs((x[b] + sides[b] <= x[a] + base * (1 - right_of[a, b]) for a, b in pairs), name="right_of_rule")
    model.addConstrs((y[a] + sides[a] <= y[b] + base * (1 - below[a, b]) for a, b in pairs), name="below_rule")
    model.addConstrs((y[b] + sides[b] <= y[a] + base * (1 - above[a, b]) for a, b in pairs), name="above_rule")

    # No two squares overlap: for each pair, at least one of the four placements holds.
    model.addConstrs((left_of[a, b] + right_of[a, b] + below[a, b] + above[a, b] >= 1 for a, b in pairs),
                     name="no_overlap")

    # No objective: any placement that meets the constraints answers the puzzle.
    return model, {"x_coords": [x[i] for i in squares], "y_coords": [y[i] for i in squares]}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.Params.OutputFlag = 0  # no solver log
    model.optimize()

    if model.Status == GRB.OPTIMAL:  # a solution
        # a variable's value is var.X, an expression's is expr.getValue(); both read through LinExpr
        value = np.vectorize(lambda out: round(gp.LinExpr(out).getValue()))
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution, Gurobi status", model.Status)  # 3 infeasible, 4 infeasible or unbounded
