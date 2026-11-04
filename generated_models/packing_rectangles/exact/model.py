# packing_rectangles: an Exact (Python) model from DCP Rosetta.
# Download the `packing_rectangles.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/packing_rectangles.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python packing_rectangles.py packing_rectangles.json

from exact import Exact


def create_model(instance):
    """Rectangle packing: place rectangular items of given widths and heights, without
    overlap and without rotating them, inside a bounding rectangle of the smallest
    possible area."""
    widths = instance["widths"]    # widths[i]: the width of item i
    heights = instance["heights"]  # heights[i]: the height of item i
    n_items = len(widths)          # the number of items

    # The bounding rectangle is at least as wide as its widest item and as high as its tallest
    # item, and at most as wide and as high as all items placed side by side.
    min_x, max_x = max(widths), sum(widths)
    min_y, max_y = max(heights), sum(heights)

    solver = Exact()

    # Exact identifies its variables by name.
    # pos_x[i] and pos_y[i] are the lower left corner of item i, counted from 0; item i cannot
    # start beyond the largest bounding rectangle minus its own size.
    pos_x = [f"pos_x_{i}" for i in range(n_items)]
    pos_y = [f"pos_y_{i}" for i in range(n_items)]
    for i in range(n_items):
        solver.addVariable(pos_x[i], 0, max_x - widths[i])
        solver.addVariable(pos_y[i], 0, max_y - heights[i])

    # total_x is the width and total_y the height of the bounding rectangle.
    solver.addVariable("total_x", min_x, max_x)
    solver.addVariable("total_y", min_y, max_y)

    # Every item lies inside the bounding rectangle.
    for i in range(n_items):
        solver.addConstraint([(1, pos_x[i]), (-1, "total_x")], False, 0, True, -widths[i])
        solver.addConstraint([(1, pos_y[i]), (-1, "total_y")], False, 0, True, -heights[i])

    # No two items overlap: for each pair, one of four sides holds.
    for i in range(n_items):
        for j in range(i + 1, n_items):
            sides = []
            for name, a, b, size, axis_max in (
                    (f"left_{i}_{j}", pos_x[i], pos_x[j], widths[i], max_x),    # item i ends before item j starts
                    (f"right_{i}_{j}", pos_x[j], pos_x[i], widths[j], max_x),   # item j ends before item i starts
                    (f"below_{i}_{j}", pos_y[i], pos_y[j], heights[i], max_y),  # item i ends below where item j starts
                    (f"above_{i}_{j}", pos_y[j], pos_y[i], heights[j], max_y)): # item j ends below where item i starts
                solver.addVariable(name, 0, 1)
                # When this side is chosen, its inequality holds.
                solver.addConstraint([(1, a), (-1, b), (axis_max, name)], False, 0, True, axis_max - size)
                sides.append((1, name))
            # At least one side holds for each pair.
            solver.addConstraint(sides, True, 1)

    # width_is[w] is 1 when the bounding rectangle is w wide, and row[w] is total_y in that case
    # and 0 otherwise.
    possible_x = range(min_x, max_x + 1)
    width_is = {}
    row = {}
    for w in possible_x:
        width_is[w] = f"total_x_is_{w}"
        row[w] = f"area_row_{w}"
        solver.addVariable(width_is[w], 0, 1)
        solver.addVariable(row[w], 0, max_y)
        solver.addConstraint([(1, row[w]), (-max_y, width_is[w])], False, 0, True, 0)
        solver.addConstraint([(1, row[w]), (-1, "total_y")], False, 0, True, 0)
        solver.addConstraint([(1, row[w]), (-1, "total_y"), (-max_y, width_is[w])], True, -max_y)

    # Exactly one width is chosen, and it is total_x.
    solver.addConstraint([(1, width_is[w]) for w in possible_x], True, 1, True, 1)
    solver.addConstraint([(w, width_is[w]) for w in possible_x] + [(-1, "total_x")], True, 0, True, 0)

    # area is the area of the bounding rectangle. It holds all items, so it is at least their
    # total area.
    solver.addVariable("area", max(min_x * min_y, sum(w * h for w, h in zip(widths, heights))), max_x * max_y)

    # area is total_x times total_y: the chosen width times the height in its row.
    solver.addConstraint([(w, row[w]) for w in possible_x] + [(-1, "area")], True, 0, True, 0)

    # Minimise the area of the bounding rectangle.
    solver.setObjective([(1, "area")], minimize=True)

    return solver, {"pos_x": pos_x, "pos_y": pos_y, "total_x": "total_x", "total_y": "total_y"}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
