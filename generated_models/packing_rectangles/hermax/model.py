from hermax.model import Model


def build(instance):
    widths = instance["widths"]
    heights = instance["heights"]
    n = len(widths)

    m = Model()
    # The enclosing rectangle is at least as wide as the widest item and at
    # most as wide as all items placed side by side (likewise for height).
    max_x = sum(widths)
    max_y = sum(heights)
    total_x = m.int("total_x", max(widths), max_x)
    total_y = m.int("total_y", max(heights), max_y)

    # Bottom-left corner of each item; items stay inside the rectangle.
    pos_x = [m.int(f"pos_x_{i}", 0, max_x) for i in range(n)]
    pos_y = [m.int(f"pos_y_{i}", 0, max_y) for i in range(n)]
    for i in range(n):
        m &= (pos_x[i] + widths[i] <= total_x)
        m &= (pos_y[i] + heights[i] <= total_y)

    # No two items overlap: for each pair, one of four separations holds.
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

    # Minimise the area of the enclosing rectangle. The area is the product
    # of the two sides, so it is tied to them by looping over the width.
    area = m.int("area", max(widths) * max(heights), max_x * max_y)
    for kx in range(total_x.lb, total_x.ub + 1):
        m &= (area == kx * total_y).only_if(total_x == kx)
    m.obj += area

    return m, {"pos_x": pos_x, "pos_y": pos_y,
               "total_x": total_x, "total_y": total_y}
