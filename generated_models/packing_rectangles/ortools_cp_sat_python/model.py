# packing_rectangles: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `packing_rectangles.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/packing_rectangles.html
# Then run it on the first instance (after `pip install ortools`):
#   python packing_rectangles.py packing_rectangles.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Rectangle packing: place rectangular items of given widths and heights, without
    overlap and without rotating them, inside a bounding rectangle of the smallest
    possible area."""
    widths = instance["widths"]    # widths[i]: the width of item i
    heights = instance["heights"]  # heights[i]: the height of item i
    n = len(widths)                # number of items

    model = cp_model.CpModel()

    # total_x and total_y: the width and the height of the bounding rectangle
    total_x = model.new_int_var(max(widths), sum(widths), "total_x")
    total_y = model.new_int_var(max(heights), sum(heights), "total_y")

    # pos_x[i], pos_y[i]: the lower-left corner of item i, counted from 0
    pos_x = [model.new_int_var(0, sum(widths), f"pos_x_{i}") for i in range(n)]
    pos_y = [model.new_int_var(0, sum(heights), f"pos_y_{i}") for i in range(n)]

    # Every item lies inside the bounding rectangle.
    for i in range(n):
        model.add(pos_x[i] + widths[i] <= total_x)
        model.add(pos_y[i] + heights[i] <= total_y)

    # x_spans[i], y_spans[i]: the horizontal and vertical extent of item i, a fixed size at its position
    x_spans = [model.new_fixed_size_interval_var(pos_x[i], widths[i], f"x_span_{i}")
               for i in range(n)]
    y_spans = [model.new_fixed_size_interval_var(pos_y[i], heights[i], f"y_span_{i}")
               for i in range(n)]
    # No two items overlap.
    model.add_no_overlap_2d(x_spans, y_spans)

    # area: the area of the bounding rectangle, total_x * total_y.
    area = model.new_int_var(max(widths) * max(heights), sum(widths) * sum(heights), "area")
    model.add_multiplication_equality(area, [total_x, total_y])

    # Minimise the area of the bounding rectangle.
    model.minimize(area)

    return model, {"pos_x": pos_x, "pos_y": pos_y, "total_x": total_x, "total_y": total_y}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
