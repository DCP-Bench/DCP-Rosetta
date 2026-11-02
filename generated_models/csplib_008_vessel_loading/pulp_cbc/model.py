# csplib_008_vessel_loading: a PuLP (Python) model from DCP Rosetta.
# Download the `csplib_008_vessel_loading.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_008_vessel_loading.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python csplib_008_vessel_loading.py csplib_008_vessel_loading.json

import math

import pulp


def create_model(instance):
    """Place rectangular containers on a rectangular deck, each parallel to the sides of the
    deck and free to be turned by 90 degrees, without overlap and with the required gap
    between every two containers of classes that need one. Decide whether they all fit."""
    deck_width = instance["deck_width"]    # the width of the deck, across the vessel
    deck_length = instance["deck_length"]  # the length of the deck, along the vessel
    n = instance["n_containers"]           # the number of containers
    width = instance["width"]              # width[i]: the width of container i
    length = instance["length"]            # length[i]: the length of container i
    classes = instance["classes"]          # classes[i]: the class of container i
    separation = instance["separation"]    # separation[a][b]: the least gap between a container of class a + 1 and one of class b + 1

    problem = pulp.LpProblem("vessel_loading", pulp.LpMinimize)  # a yes or no question: no objective

    # Possible corner positions along the deck. Pushing a container left or down stops it at the deck edge or against
    # another container with the required gap, so every corner is a sum of container sides and gaps, counted from 0.
    sides = set(width) | set(length)
    gaps = {gap for row in separation for gap in row if gap >= 0} | {0}

    # the positions up to limit that are sums of sides and gaps, counted from 0
    def corner_positions(limit):
        reached = [0]
        seen = {0}
        for position in reached:
            for side in sides:
                for gap in gaps:
                    nxt = position + side + gap
                    if nxt <= limit and nxt not in seen:
                        seen.add(nxt)
                        reached.append(nxt)
        return sorted(seen)

    xs = corner_positions(deck_width)
    ys = corner_positions(deck_length)

    # Every side and gap is a multiple of unit, so the containers and their grown footprints
    # start and end on multiples of unit. Two of them overlap exactly when they share a cell
    # on that grid, so only those cells are checked.
    unit = 0
    for value in sides | gaps:
        unit = math.gcd(unit, value)
    cells = [(cx, cy) for cx in range(0, deck_width, unit) for cy in range(0, deck_length, unit)]

    # place[i] holds the placements of container i. place[i][(w, h, x, y)] is 1 when container i
    # sits with its left side at x and its bottom side at y, w across the deck and h along it.
    place = []
    for i in range(n):
        shapes = [(width[i], length[i])]
        if width[i] != length[i]:  # a square container covers the same cells when turned
            shapes.append((length[i], width[i]))
        # the placements of container i that fit on the deck
        options = {}
        for w, h in shapes:
            for x in xs:
                for y in ys:
                    if x + w <= deck_width and y + h <= deck_length:
                        options[(w, h, x, y)] = pulp.LpVariable(f"place_{i}_{w}x{h}_{x}_{y}", cat="Binary")
        place.append(options)
        # container i is placed exactly once
        problem += pulp.lpSum(options.values()) == 1

    # cover[(i, cx, cy)] lists the placements of container i that include the cell (cx, cy)
    cover = {}
    for i in range(n):
        for cx, cy in cells:
            cover[(i, cx, cy)] = [var for (w, h, x, y), var in place[i].items()
                                  if x <= cx < x + w and y <= cy < y + h]
    # no cell of the deck lies under two containers
    for cx, cy in cells:
        problem += pulp.lpSum(var for i in range(n) for var in cover[(i, cx, cy)]) <= 1

    # Separation. Containers a and b of classes that need a gap sep > 0 are at least sep apart,
    # along the deck or across it. They break that rule exactly when a cell of b lies inside
    # a's footprint grown by sep in every direction. So for every cell, if b covers it then a's
    # grown footprint must not contain it. Pairs whose classes need no gap are skipped.
    for a in range(n):
        for b in range(a + 1, n):
            sep = separation[classes[a] - 1][classes[b] - 1]
            if sep <= 0:
                continue
            for cx, cy in cells:
                # the placements of a whose grown footprint contains the cell
                grown = [var for (w, h, x, y), var in place[a].items()
                         if x - sep <= cx <= x + w - 1 + sep and y - sep <= cy <= y + h - 1 + sep]
                problem += pulp.lpSum(grown) + pulp.lpSum(cover[(b, cx, cy)]) <= 1

    # left[i]: the x coordinate of the left side of container i
    left = [pulp.lpSum(x * var for (w, h, x, y), var in place[i].items()) for i in range(n)]
    # right[i]: the x coordinate of the right side of container i
    right = [pulp.lpSum((x + w) * var for (w, h, x, y), var in place[i].items()) for i in range(n)]
    # top[i]: the y coordinate of the top side of container i
    top = [pulp.lpSum((y + h) * var for (w, h, x, y), var in place[i].items()) for i in range(n)]
    # bottom[i]: the y coordinate of the bottom side of container i
    bottom = [pulp.lpSum(y * var for (w, h, x, y), var in place[i].items()) for i in range(n)]

    return problem, {"left": left, "right": right, "top": top, "bottom": bottom}


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
