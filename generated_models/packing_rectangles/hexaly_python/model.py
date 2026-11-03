"""Rectangle packing: place the items without overlap in the smallest-area enclosing rectangle."""
import hexaly.optimizer as hx


def build(instance):
    widths, heights = instance["widths"], instance["heights"]
    n = len(widths)
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # The enclosing rectangle is at least as wide as the widest item and at most all items side by side
    total_x = model.int(max(widths), sum(widths))
    total_y = model.int(max(heights), sum(heights))
    pos_x = [model.int(0, sum(widths)) for _ in range(n)]
    pos_y = [model.int(0, sum(heights)) for _ in range(n)]

    # Every item lies inside the enclosing rectangle
    for i in range(n):
        model.constraint(pos_x[i] + widths[i] <= total_x)
        model.constraint(pos_y[i] + heights[i] <= total_y)
    # No two items overlap: one lies left of, right of, below or above the other
    for i in range(n):
        for j in range(i + 1, n):
            model.constraint(model.or_(pos_x[i] + widths[i] <= pos_x[j], pos_x[j] + widths[j] <= pos_x[i],
                                       pos_y[i] + heights[i] <= pos_y[j], pos_y[j] + heights[j] <= pos_y[i]))

    # Minimise the area of the enclosing rectangle; implied, it holds the items' total area
    area = total_x * total_y
    model.constraint(area >= sum(w * h for w, h in zip(widths, heights)))
    model.minimize(area)
    return optimizer, {"pos_x": pos_x, "pos_y": pos_y, "total_x": total_x, "total_y": total_y}
