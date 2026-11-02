"""Perfect square placement: pack the given squares into the base square with no overlap and no spare space."""
import hexaly.optimizer as hx


def build(instance):
    base, sides = instance["base"], instance["sides"]
    n = len(sides)
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # (x[i], y[i]) is the lower-left corner of square i, which must lie inside the base square
    x = [model.int(0, base - sides[i]) for i in range(n)]
    y = [model.int(0, base - sides[i]) for i in range(n)]

    # No two squares overlap: one lies left of, right of, below or above the other
    for i in range(n):
        for j in range(i + 1, n):
            model.constraint(model.or_(x[i] + sides[i] <= x[j], x[j] + sides[j] <= x[i],
                                       y[i] + sides[i] <= y[j], y[j] + sides[j] <= y[i]))

    # Implied by a packing without spare space: every column and every row of unit cells is
    # covered exactly, so the sides of the squares crossing it add up to the base
    for c in range(base):
        model.constraint(model.sum(sides[i] * model.and_(x[i] <= c, c < x[i] + sides[i]) for i in range(n)) == base)
        model.constraint(model.sum(sides[i] * model.and_(y[i] <= c, c < y[i] + sides[i]) for i in range(n)) == base)

    return optimizer, {"x_coords": x, "y_coords": y}
