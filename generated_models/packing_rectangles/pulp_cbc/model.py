# packing_rectangles: a PuLP (Python) model from DCP Rosetta.
# Download the `packing_rectangles.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/packing_rectangles.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python packing_rectangles.py packing_rectangles.json

import pulp


def create_model(instance):
    """Packing rectangles: place rectangular items (given widths and heights, no rotation)
    inside a larger rectangle so that no two items overlap and all items lie within it.
    Minimise the area of the larger rectangle."""
    widths = instance["widths"]    # widths[i]: the width of item i
    heights = instance["heights"]  # heights[i]: the height of item i

    n_items = len(widths)  # number of items
    item_area = sum(w * h for w, h in zip(widths, heights))  # total area of the items

    # min_x, max_x: the smallest and largest width of the larger rectangle. The widest item
    # sets the smallest, and all items side by side set the largest. min_y, max_y do the same
    # for the height, with the tallest item and all items stacked.
    min_x, max_x = max(widths), sum(widths)
    min_y, max_y = max(heights), sum(heights)

    problem = pulp.LpProblem("packing_rectangles", pulp.LpMinimize)

    # pos_x[i], pos_y[i]: the lower-left corner of item i, measured from the lower-left
    # corner of the larger rectangle
    pos_x = [pulp.LpVariable(f"pos_x_{i}", 0, max_x, cat="Integer") for i in range(n_items)]
    pos_y = [pulp.LpVariable(f"pos_y_{i}", 0, max_y, cat="Integer") for i in range(n_items)]

    # total_x, total_y: the width and the height of the larger rectangle
    total_x = pulp.LpVariable("total_x", min_x, max_x, cat="Integer")
    total_y = pulp.LpVariable("total_y", min_y, max_y, cat="Integer")

    # Every item lies inside the larger rectangle.
    for i in range(n_items):
        problem += pos_x[i] + widths[i] <= total_x
        problem += pos_y[i] + heights[i] <= total_y

    # No two items overlap. For each pair, side[k] is 1 when the pair is placed the k-th way:
    # item i left of item j, item j left of item i, item i below item j, or item j below item i.
    # A way that is not chosen is satisfied by any placement inside the larger rectangle.
    for i in range(n_items):
        for j in range(i + 1, n_items):
            side = [pulp.LpVariable(f"side_{i}_{j}_{k}", cat="Binary") for k in range(4)]
            problem += pos_x[i] + widths[i] <= pos_x[j] + max_x * (1 - side[0])
            problem += pos_x[j] + widths[j] <= pos_x[i] + max_x * (1 - side[1])
            problem += pos_y[i] + heights[i] <= pos_y[j] + max_y * (1 - side[2])
            problem += pos_y[j] + heights[j] <= pos_y[i] + max_y * (1 - side[3])
            # At least one way holds for every pair.
            problem += pulp.lpSum(side) >= 1
            # Two items side by side need the larger rectangle to be at least as wide as
            # their two widths together. Two items stacked need it to be at least as tall
            # as their two heights together.
            problem += total_x >= (widths[i] + widths[j]) * (side[0] + side[1])
            problem += total_y >= (heights[i] + heights[j]) * (side[2] + side[3])

    # The area is total_x * total_y. wide[x] is 1 when the larger rectangle is x wide, and
    # tall[x] is its height when it is x wide, and 0 otherwise. So the area is the sum of
    # x * tall[x].
    wide = {x: pulp.LpVariable(f"wide_{x}", cat="Binary") for x in range(min_x, max_x + 1)}
    tall = {x: pulp.LpVariable(f"tall_{x}", 0, max_y) for x in wide}
    problem += pulp.lpSum(wide.values()) == 1
    problem += total_x == pulp.lpSum(x * wide[x] for x in wide)
    problem += total_y == pulp.lpSum(tall.values())
    for x in wide:
        # The height is zero unless the width is x. When it is, the items' total area fits
        # in x times the height, so the height is at least that area divided by x, rounded
        # up, and at least the tallest item.
        problem += tall[x] <= max_y * wide[x]
        problem += tall[x] >= max(min_y, -(-item_area // x)) * wide[x]

    # Minimise the area of the larger rectangle.
    problem += pulp.lpSum(x * tall[x] for x in wide)

    return problem, {"pos_x": pos_x, "pos_y": pos_y, "total_x": total_x, "total_y": total_y}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
