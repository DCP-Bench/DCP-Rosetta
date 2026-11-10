# packing_rectangles: a hermax (Python) model from DCP Rosetta.
# Download the `packing_rectangles.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/packing_rectangles.html
# Then run it on the first instance (after `pip install hermax`):
#   python packing_rectangles.py packing_rectangles.json

from hermax.model import Model


def create_model(instance):
    """Place non-overlapping axis-aligned rectangles (no rotation) inside the smallest
    enclosing rectangle, minimising that rectangle's area. Positions are 0-based
    bottom-left corners."""
    # instance["widths"][i]: width of rectangle i
    widths = instance["widths"]
    # instance["heights"][i]: height of rectangle i
    heights = instance["heights"]
    n = len(widths)  # number of rectangles

    m = Model()

    # total_x, total_y: width and height of the enclosing rectangle. It must be at least
    # as wide as the widest item and at most as wide as all items side by side (a wider
    # rectangle only adds area, so it never helps the minimum-area objective).
    total_x = m.int("total_x", max(widths), sum(widths))
    total_y = m.int("total_y", max(heights), sum(heights))

    # pos_x[i], pos_y[i]: bottom-left corner of rectangle i, 0-based
    pos_x = [m.int(f"pos_x_{i}", 0, sum(widths) - widths[i]) for i in range(n)]
    pos_y = [m.int(f"pos_y_{i}", 0, sum(heights) - heights[i]) for i in range(n)]

    # Every rectangle lies inside the enclosing rectangle.
    for i in range(n):
        m &= (pos_x[i] + widths[i] <= total_x)
        m &= (pos_y[i] + heights[i] <= total_y)

    # No two rectangles overlap: for each pair, one of four separations holds.
    # left[i][j] is true when i is entirely left of j, right[i][j] when i is entirely
    # right of j, below[i][j] when i is entirely below j, above[i][j] when i is above j.
    for i in range(n):
        for j in range(i + 1, n):
            left = m.bool()
            right = m.bool()
            below = m.bool()
            above = m.bool()
            m &= (pos_x[i] + widths[i] <= pos_x[j]).iff(left)
            m &= (pos_x[j] + widths[j] <= pos_x[i]).iff(right)
            m &= (pos_y[i] + heights[i] <= pos_y[j]).iff(below)
            m &= (pos_y[j] + heights[j] <= pos_y[i]).iff(above)
            m &= (left | right | below | above)

    # area: the area of the enclosing rectangle, total_x * total_y. Multiplying two
    # integer variables is not supported, so the product is tied to total_x by a case
    # per possible width kx: when the width is kx, the area is kx times the height.
    area = m.int("area", max(widths) * max(heights), sum(widths) * sum(heights))
    for kx in range(total_x.lb, total_x.ub + 1):
        m &= (area == kx * total_y).only_if(total_x == kx)

    # Minimise the area of the enclosing rectangle.
    m.obj += area

    # The objective in the problem's terms: the area of the enclosing rectangle, the cost minimised above.
    return m, {"pos_x": pos_x, "pos_y": pos_y, "total_x": total_x, "total_y": total_y}, area


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
        print("objective =", result[objective])
    else:
        print("No solution:", result.status)
