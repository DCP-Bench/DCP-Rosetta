# packing_rectangles: a PyCSP3 model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/packing_rectangles.html
# Download the `packing_rectangles.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/packing_rectangles.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python packing_rectangles.py packing_rectangles.json

from pycsp3 import *


def create_model(instance):
    """Rectangular items are placed inside a larger rectangle so that no two items overlap
    and every item lies within the larger rectangle. Minimise the area of the larger rectangle."""
    widths = instance["widths"]    # widths[i] is the width of item i
    heights = instance["heights"]  # heights[i] is the height of item i
    n_items = len(widths)

    # The items laid side by side in one row bound the width of the larger rectangle, and
    # the items stacked in one column bound its height. The bounds are taken as holding for
    # an optimal packing, so no solution with a wider or taller container is lost.
    width_bound = sum(widths)
    height_bound = sum(heights)

    # total_x is the width of the larger rectangle.
    total_x = Var(dom=range(1, width_bound + 1))
    # total_y is the height of the larger rectangle.
    total_y = Var(dom=range(1, height_bound + 1))

    # pos_x[i] is the horizontal position of the left edge of item i, counted from 0.
    # An item lies inside the container, so its left edge is below width_bound.
    pos_x = VarArray(size=n_items, dom=range(width_bound))
    # pos_y[i] is the vertical position of the bottom edge of item i, counted from 0.
    # An item lies inside the container, so its bottom edge is below height_bound.
    pos_y = VarArray(size=n_items, dom=range(height_bound))

    satisfy(
        # Every item lies within the larger rectangle. The items are not rotated,
        # since the statement mentions no rotation.
        [pos_x[i] + widths[i] <= total_x for i in range(n_items)],
        [pos_y[i] + heights[i] <= total_y for i in range(n_items)],
        # No two items overlap.
        NoOverlap(
            origins=[(pos_x[i], pos_y[i]) for i in range(n_items)],
            lengths=[(widths[i], heights[i]) for i in range(n_items)],
        ),
    )

    # The area of the larger rectangle is minimised.
    minimize(total_x * total_y)

    return {"pos_x": pos_x, "pos_y": pos_y, "total_x": total_x, "total_y": total_y}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is OPTIMUM:
        print("pos_x", "=", values(outputs["pos_x"]))
        print("pos_y", "=", values(outputs["pos_y"]))
        print("total_x", "=", value(outputs["total_x"]))
        print("total_y", "=", value(outputs["total_y"]))
    else:
        print("No solution:", status())
