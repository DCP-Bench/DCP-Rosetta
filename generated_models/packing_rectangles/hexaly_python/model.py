"""Rectangle packing: place the items without overlap in the smallest-area enclosing rectangle."""
import hexaly.optimizer as hx


def build(instance):
    widths, heights = instance["widths"], instance["heights"]  # widths[i], heights[i] = x and y extent of item i
    n = len(widths)  # number of items
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # total_x, total_y = width and height of the larger rectangle that holds all items.
    # Bounds: at least as wide (tall) as the widest (tallest) item, and at most all items side by side (stacked)
    total_x = model.int(max(widths), sum(widths))
    total_y = model.int(max(heights), sum(heights))
    # pos_x[i], pos_y[i] = where item i starts, counted from 0: it spans pos_x[i] to pos_x[i] + widths[i]
    # in x and pos_y[i] to pos_y[i] + heights[i] in y. Upper bounds are the same as for total_x and total_y
    pos_x = [model.int(0, sum(widths)) for _ in range(n)]
    pos_y = [model.int(0, sum(heights)) for _ in range(n)]

    # All items are within the boundaries of the larger rectangle
    for i in range(n):
        model.constraint(pos_x[i] + widths[i] <= total_x)
        model.constraint(pos_y[i] + heights[i] <= total_y)
    # No two items overlap: for every pair, one lies left of, right of, below or above the other
    for i in range(n):
        for j in range(i + 1, n):
            model.constraint(model.or_(pos_x[i] + widths[i] <= pos_x[j], pos_x[j] + widths[j] <= pos_x[i],
                                       pos_y[i] + heights[i] <= pos_y[j], pos_y[j] + heights[j] <= pos_y[i]))

    # area = total area of the larger rectangle
    area = total_x * total_y
    # Implied by the rules above: the larger rectangle holds all items, so its area is at least the sum of their areas
    model.constraint(area >= sum(w * h for w, h in zip(widths, heights)))
    # Minimise the total area of the larger rectangle required to pack all the items
    model.minimize(area)
    return optimizer, {"pos_x": pos_x, "pos_y": pos_y, "total_x": total_x, "total_y": total_y}
