# Perfect square placement (CSPLib 009): pack the given squares into a base x base square with
# no overlap and sides parallel to the border. The areas add up to base^2, so the squares tile
# the big square exactly. Output: the bottom-left corner (x, y) of each square, from 0.
import mip


def build(instance):
    base = instance["base"]
    sides = instance["sides"]
    n = len(sides)
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # place[s][(x, y)] = 1 when square s has its corner at (x, y); it must lie inside the big square
    place = []
    for s in range(n):
        span = range(base - sides[s] + 1)
        place.append({(x, y): model.add_var(f"p_{s}_{x}_{y}", var_type=mip.BINARY) for x in span for y in span})

    # every square is placed exactly once
    for s in range(n):
        model += mip.xsum(place[s].values()) == 1

    # every cell of the big square is covered by exactly one square: no overlap, and since the
    # areas add up to base^2, no gap either
    covers = {(a, b): [] for a in range(base) for b in range(base)}
    for s in range(n):
        k = sides[s]
        for (x, y), v in place[s].items():
            for a in range(x, x + k):
                for b in range(y, y + k):
                    covers[a, b].append(v)
    for cell, vs in covers.items():
        model += mip.xsum(vs) == 1

    # the coordinates of each square, read from its placement
    xs, ys = [], []
    for s in range(n):
        top = base - sides[s]
        x = model.add_var(f"x_{s}", lb=0, ub=top, var_type=mip.INTEGER)
        y = model.add_var(f"y_{s}", lb=0, ub=top, var_type=mip.INTEGER)
        model += x == mip.xsum(px * v for (px, py), v in place[s].items())
        model += y == mip.xsum(py * v for (px, py), v in place[s].items())
        xs.append(x)
        ys.append(y)

    return model, {"x_coords": xs, "y_coords": ys}
