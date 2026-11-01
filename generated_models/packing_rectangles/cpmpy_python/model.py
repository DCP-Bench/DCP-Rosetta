# packing_rectangles: a CPMpy model from DCP Rosetta.
# Download the `packing_rectangles.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/packing_rectangles.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python packing_rectangles.py packing_rectangles.json

import cpmpy as cp
import numpy as np


def create_model(instance):
    """Rectangle packing: place rectangular items of given widths and heights, without
    overlap, inside a bounding rectangle of the smallest possible area."""
    widths = np.array(instance["widths"])    # widths[i]: the width of item i
    heights = np.array(instance["heights"])  # heights[i]: the height of item i
    n = len(widths)

    # The bounding rectangle is at least as wide (high) as the widest (highest) item,
    # and never wider (higher) than all items side by side (stacked), which always fits.
    min_x, max_x = widths.max(), widths.sum()
    min_y, max_y = heights.max(), heights.sum()

    # (pos_x[i], pos_y[i]) is the lower-left corner of item i, counted from 0
    pos_x = cp.intvar(0, max_x, shape=n, name="pos_x")
    pos_y = cp.intvar(0, max_y, shape=n, name="pos_y")

    # total_x and total_y are the width and the height of the bounding rectangle
    total_x = cp.intvar(min_x, max_x, name="total_x")
    total_y = cp.intvar(min_y, max_y, name="total_y")

    model = cp.Model()

    # Every item lies inside the bounding rectangle.
    model.add(pos_x + widths <= total_x)
    model.add(pos_y + heights <= total_y)

    # No two items overlap: one lies entirely to the left of, to the right of, below, or above the other.
    for i in range(n):
        for j in range(i + 1, n):
            model.add((pos_x[i] + widths[i] <= pos_x[j])
                      | (pos_x[j] + widths[j] <= pos_x[i])
                      | (pos_y[i] + heights[i] <= pos_y[j])
                      | (pos_y[j] + heights[j] <= pos_y[i]))

    # Minimise the area of the bounding rectangle.
    model.minimize(total_x * total_y)

    return model, {"pos_x": pos_x, "pos_y": pos_y, "total_x": total_x, "total_y": total_y}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
