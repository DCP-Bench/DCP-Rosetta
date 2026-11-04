# packing_rectangles: a Z3 (Python) model from DCP Rosetta.
# Download the `packing_rectangles.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/packing_rectangles.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python packing_rectangles.py packing_rectangles.json

import z3


def create_model(instance):
    """Rectangle packing: place rectangular items of the given widths and heights, without
    overlap and without rotating them, inside an enclosing rectangle of the smallest
    possible area."""
    widths = instance["widths"]    # widths[i]: the width of item i
    heights = instance["heights"]  # heights[i]: the height of item i
    n_items = len(widths)          # number of items

    # total_x, total_y: the width and the height of the enclosing rectangle
    total_x, total_y = z3.Ints("total_x total_y")

    # pos_x[i], pos_y[i]: the lower-left corner of item i, counted from 0
    pos_x = [z3.Int(f"pos_x_{i}") for i in range(n_items)]
    pos_y = [z3.Int(f"pos_y_{i}") for i in range(n_items)]

    solver = z3.Optimize()

    # The enclosing rectangle is no narrower than its widest item and no wider than all
    # items side by side; the same holds for height and items stacked.
    solver.add(total_x >= max(widths), total_x <= sum(widths),
               total_y >= max(heights), total_y <= sum(heights))

    # Every item lies completely inside the enclosing rectangle.
    for i in range(n_items):
        solver.add(pos_x[i] >= 0, pos_y[i] >= 0,
                   pos_x[i] + widths[i] <= total_x, pos_y[i] + heights[i] <= total_y)

    # No two items overlap: one lies entirely to the left of, to the right of, below or above the other.
    for i in range(n_items):
        for j in range(i + 1, n_items):
            solver.add(z3.Or(pos_x[i] + widths[i] <= pos_x[j],
                             pos_x[j] + widths[j] <= pos_x[i],
                             pos_y[i] + heights[i] <= pos_y[j],
                             pos_y[j] + heights[j] <= pos_y[i]))

    # The area of the enclosing rectangle, to be as small as possible.
    area = total_x * total_y

    solver.minimize(area)

    return solver, {"pos_x": pos_x, "pos_y": pos_y, "total_x": total_x, "total_y": total_y}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
