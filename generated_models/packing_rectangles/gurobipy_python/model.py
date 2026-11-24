# packing_rectangles: a Gurobi (Python) model from DCP Rosetta.
# Download the `packing_rectangles.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/packing_rectangles.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python packing_rectangles.py packing_rectangles.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Pack rectangles of given widths and heights, without overlap, into an enclosing rectangle of least area."""
    widths = instance["widths"]  # widths[i]: the width of rectangle i
    heights = instance["heights"]  # heights[i]: the height of rectangle i
    n = len(widths)
    items = range(n)

    # Bounds on the enclosing rectangle, not stated in the problem: its width is at least the
    # widest rectangle and at most the widths added up. The upper bound cuts off no optimum:
    # pushing every rectangle left until it touches the edge or another rectangle never widens the
    # enclosing rectangle, and then it is no wider than all the rectangles side by side. The
    # height is bounded likewise, pushing down.
    min_x, max_x = max(widths), sum(widths)
    min_y, max_y = max(heights), sum(heights)

    model = gp.Model("packing_rectangles")

    # pos_x[i] and pos_y[i] are the left and bottom edges of rectangle i, counted from 0.
    pos_x = model.addVars(items, lb=0, ub=max_x, vtype=GRB.INTEGER, name="pos_x")
    pos_y = model.addVars(items, lb=0, ub=max_y, vtype=GRB.INTEGER, name="pos_y")
    # total_x and total_y are the width and the height of the enclosing rectangle.
    total_x = model.addVar(lb=min_x, ub=max_x, vtype=GRB.INTEGER, name="total_x")
    total_y = model.addVar(lb=min_y, ub=max_y, vtype=GRB.INTEGER, name="total_y")

    # Every rectangle lies within the enclosing rectangle.
    model.addConstrs((pos_x[i] + widths[i] <= total_x for i in items), name="inside_x")
    model.addConstrs((pos_y[i] + heights[i] <= total_y for i in items), name="inside_y")

    # No overlap: every pair of rectangles is side by side or one above the other.
    # side[i, j, k] is 1 when the pair is apart in the k-th way: 0 means i is left of j,
    # 1 means j is left of i, 2 means i is below j, 3 means j is below i. At least one holds.
    pairs = [(i, j) for i in items for j in items if i < j]
    side = model.addVars(pairs, range(4), vtype=GRB.BINARY, name="side")
    model.addConstrs(((side[i, j, 0] == 1) >> (pos_x[i] + widths[i] <= pos_x[j]) for i, j in pairs))
    model.addConstrs(((side[i, j, 1] == 1) >> (pos_x[j] + widths[j] <= pos_x[i]) for i, j in pairs))
    model.addConstrs(((side[i, j, 2] == 1) >> (pos_y[i] + heights[i] <= pos_y[j]) for i, j in pairs))
    model.addConstrs(((side[i, j, 3] == 1) >> (pos_y[j] + heights[j] <= pos_y[i]) for i, j in pairs))
    model.addConstrs((side.sum(i, j, "*") >= 1 for i, j in pairs), name="apart")

    # The area of the enclosing rectangle is total_x * total_y. Gurobi accepts that product
    # directly, but it is written linearly so that the model stays a MIP: the width is chosen
    # from its possible values: width_is[w] is 1 when the enclosing width is w, and part[w]
    # stands for width_is[w] * total_y, which the four constraints below force (part[w] is
    # total_y when w is the width, and 0 otherwise).
    widths_range = range(min_x, max_x + 1)
    width_is = model.addVars(widths_range, vtype=GRB.BINARY, name="width_is")
    part = model.addVars(widths_range, lb=0, ub=max_y, vtype=GRB.CONTINUOUS, name="part")
    model.addConstr(width_is.sum() == 1, name="one_width")
    model.addConstr(total_x == gp.quicksum(w * width_is[w] for w in widths_range), name="width_value")
    model.addConstrs((part[w] <= max_y * width_is[w] for w in widths_range), name="part_hi")
    model.addConstrs((part[w] >= min_y * width_is[w] for w in widths_range), name="part_lo")
    model.addConstrs((part[w] <= total_y - min_y * (1 - width_is[w]) for w in widths_range), name="part_le_total")
    model.addConstrs((part[w] >= total_y - max_y * (1 - width_is[w]) for w in widths_range), name="part_ge_total")
    area = gp.quicksum(w * part[w] for w in widths_range)  # the area total_x * total_y

    # The area of the enclosing rectangle is total_x * total_y, a product of two variables, which
    # is not linear. So the width is chosen from its possible values: width_is[w] is 1 when the
    # enclosing width is w, and part[w] stands for width_is[w] * total_y, which the four
    # constraints below force (part[w] is total_y when w is the width, and 0 otherwise).
    widths_range = range(min_x, max_x + 1)
    width_is = model.addVars(widths_range, vtype=GRB.BINARY, name="width_is")
    part = model.addVars(widths_range, lb=0, ub=max_y, vtype=GRB.CONTINUOUS, name="part")
    model.addConstr(width_is.sum() == 1, name="one_width")
    model.addConstr(total_x == gp.quicksum(w * width_is[w] for w in widths_range), name="width_value")
    for w in widths_range:
        model.addConstr(part[w] <= max_y * width_is[w])
        model.addConstr(part[w] >= min_y * width_is[w])
        model.addConstr(part[w] <= total_y - min_y * (1 - width_is[w]))
        model.addConstr(part[w] >= total_y - max_y * (1 - width_is[w]))
    area = gp.quicksum(w * part[w] for w in widths_range)  # the area total_x * total_y

    # A redundant constraint, not in the statement: the enclosing rectangle is at least as large
    # as the rectangles together.
    model.addConstr(area >= sum(widths[i] * heights[i] for i in items), name="area_bound")

    # Objective: minimise the area of the enclosing rectangle.
    model.setObjective(area, GRB.MINIMIZE)

    # Outputs: the lower-left corners of the rectangles as lists, and the enclosing width and height.
    return model, {
        "pos_x": [pos_x[i] for i in items],
        "pos_y": [pos_y[i] for i in items],
        "total_x": total_x,
        "total_y": total_y,
    }


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.Params.OutputFlag = 0  # no solver log
    model.Params.MIPGap = 0  # prove the optimum; the default stops within 0.01% of it
    model.optimize()

    if model.Status == GRB.OPTIMAL:  # a proven optimum
        print("Objective value:", round(model.ObjVal))
        # a variable's value is var.X, an expression's is expr.getValue(); both read through LinExpr
        value = np.vectorize(lambda out: round(gp.LinExpr(out).getValue()))
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution, Gurobi status", model.Status)  # 3 infeasible, 4 infeasible or unbounded
