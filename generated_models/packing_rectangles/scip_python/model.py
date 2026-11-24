# packing_rectangles: a SCIP (Python) model from DCP Rosetta.
# Download the `packing_rectangles.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/packing_rectangles.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python packing_rectangles.py packing_rectangles.json

from pyscipopt import Model


def create_model(instance):
    """Place rectangular items in a larger rectangle without overlaps and without
    turning them, so that the larger rectangle has the least possible area."""
    widths = instance["widths"]    # widths[i]: the width of item i (along x)
    heights = instance["heights"]  # heights[i]: the height of item i (along y)
    n = len(widths)                # the number of items
    items = range(n)

    model = Model("packing_rectangles")

    # total_x, total_y: the width and height of the large rectangle (outputs).
    # Lower bound: the large rectangle is at least as wide as the widest item and
    # at least as tall as the tallest item.
    # Upper bound: pushing the items to the left and down never enlarges the
    # rectangle. In a packing pushed that far, the width is covered by a chain of
    # items placed end to end from the left edge to the right edge, so it is at
    # most sum(widths); the height is at most sum(heights) by the same argument.
    # So an optimal rectangle is no wider or taller than that.
    total_x = model.addVar(vtype="I", lb=max(widths), ub=sum(widths), name="total_x")
    total_y = model.addVar(vtype="I", lb=max(heights), ub=sum(heights), name="total_y")

    # x[i], y[i]: the position of the lower-left corner of item i (outputs), counted
    # from the lower-left corner of the large rectangle, which is (0, 0).
    # Upper bound: an optimal rectangle is at most sum(widths) wide (see total_x),
    # so item i's corner is at most sum(widths) minus its own width, and likewise
    # for y.
    x = [model.addVar(vtype="I", lb=0, ub=sum(widths) - widths[i], name=f"x_{i}") for i in items]
    y = [model.addVar(vtype="I", lb=0, ub=sum(heights) - heights[i], name=f"y_{i}") for i in items]

    # left[i, j] = 1 when item i lies entirely to the left of item j.
    # below[i, j] = 1 when item i lies entirely below item j.
    # An item is not left of or below itself, so the diagonal is fixed to 0.
    no_self = [[0 if i == j else 1 for j in items] for i in items]
    left = model.addMatrixVar((n, n), vtype="B", ub=no_self, name="left")
    below = model.addMatrixVar((n, n), vtype="B", ub=no_self, name="below")

    # Each item lies inside the large rectangle: its right edge is at most total_x
    # and its top edge is at most total_y.
    for i in items:
        model.addCons(x[i] + widths[i] <= total_x)
        model.addCons(y[i] + heights[i] <= total_y)

    # When left[i, j] = 1, item i's right edge is at or left of item j's left edge.
    # When below[i, j] = 1, item i's top edge is at or below item j's bottom edge.
    # Each is an indicator, because it only applies when its binary is 1.
    for i in items:
        for j in items:
            if i != j:
                model.addConsIndicator(x[i] + widths[i] <= x[j], binvar=left[i, j])
                model.addConsIndicator(y[i] + heights[i] <= y[j], binvar=below[i, j])

    # No overlaps: for each pair of items, one lies entirely to the left of the
    # other, or one lies entirely below the other.
    for i in items:
        for j in range(i + 1, n):
            model.addCons(left[i, j] + left[j, i] + below[i, j] + below[j, i] >= 1)

    # area: the area of the large rectangle, total_x * total_y. The product of two
    # variables is nonlinear, and setObjective takes only linear expressions, so the
    # product is held in the integer variable area, and area is the objective.
    # Bounds: area is total_x * total_y with total_x and total_y within the bounds
    # above, so it lies between their smallest and their largest products.
    area = model.addVar(vtype="I", lb=max(widths) * max(heights),
                        ub=sum(widths) * sum(heights), name="area")
    model.addCons(area == total_x * total_y)

    # Objective: minimise the area of the large rectangle. total_x and total_y only
    # need to be at least the right and top edges of the items; the objective makes
    # them exact, because a larger rectangle has a larger area.
    model.setObjective(area, "minimize")

    return model, {"pos_x": x, "pos_y": y, "total_x": total_x, "total_y": total_y}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
