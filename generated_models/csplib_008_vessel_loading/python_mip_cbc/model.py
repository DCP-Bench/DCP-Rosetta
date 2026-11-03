# csplib_008_vessel_loading: a Python-MIP (Python) model from DCP Rosetta.
# Download the `csplib_008_vessel_loading.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_008_vessel_loading.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python csplib_008_vessel_loading.py csplib_008_vessel_loading.json

import mip


def create_model(instance):
    """Decide whether the containers can be placed on the deck without overlapping
    and with the required distance between each pair of classes."""
    deck_width = instance["deck_width"]        # the width of the deck, across it
    deck_length = instance["deck_length"]      # the length of the deck, along it
    n_containers = instance["n_containers"]    # the number of containers
    width = instance["width"]                  # width[i]: the width of container i
    length = instance["length"]                # length[i]: the length of container i
    classes = instance["classes"]              # classes[i]: the class of container i, numbered from 1
    separation = instance["separation"]        # separation[a - 1][b - 1]: the least distance between classes a and b

    model = mip.Model(solver_name="CBC")

    # Distances a container edge can be pushed by: the container sides and the positive separations.
    steps = set(width) | set(length)
    for row in separation:
        steps.update(gap for gap in row if gap > 0)

    # Edge positions a container can take. A container is pushed toward the corner until it meets
    # the deck edge, or another container plus a gap, so each position is a sum of steps.
    def reachable(limit):
        reach = {0}
        frontier = [0]
        while frontier:
            p = frontier.pop()
            for s in steps:
                q = p + s
                if q <= limit and q not in reach:
                    reach.add(q)
                    frontier.append(q)
        return sorted(reach)

    xs = reachable(deck_width)   # left-edge positions across the deck
    ys = reachable(deck_length)  # bottom-edge positions along the deck

    # placements[i] lists the places container i can take as (ew, eh, x0, y0, p). The container covers
    # ew cells across the deck and eh cells along it, from x0 and y0. p is 1 when it takes this place.
    placements = []
    for i in range(n_containers):
        wi = width[i]
        li = length[i]
        # A square container has one orientation only; any other container may be turned.
        orients = [(wi, li)] if wi == li else [(wi, li), (li, wi)]
        plist = []
        for ew, eh in orients:
            for x0 in xs:
                if x0 + ew > deck_width:
                    continue
                for y0 in ys:
                    if y0 + eh > deck_length:
                        continue
                    p = model.add_var(name=f"p_{i}_{ew}_{eh}_{x0}_{y0}", var_type=mip.BINARY)
                    plist.append((ew, eh, x0, y0, p))
        placements.append(plist)
        # Each container takes exactly one place.
        model.add_constr(mip.xsum(p for (_, _, _, _, p) in plist) == 1, name=f"place_{i}")

    # Each deck cell is covered by at most one container.
    for cx in range(deck_width):
        for cy in range(deck_length):
            terms = []
            for i in range(n_containers):
                for ew, eh, x0, y0, p in placements[i]:
                    if x0 <= cx < x0 + ew and y0 <= cy < y0 + eh:
                        terms.append(p)
            if len(terms) > 1:
                model.add_constr(mip.xsum(terms) <= 1, name=f"cell_{cx}_{cy}")

    # Containers of two classes stay apart by the required distance, across the deck or along it.
    # Container i grown by the distance on every side must not cover any cell that container j covers.
    for i in range(n_containers):
        for j in range(i + 1, n_containers):
            gap = max(separation[classes[i] - 1][classes[j] - 1], separation[classes[j] - 1][classes[i] - 1])
            if gap <= 0:
                continue
            for cx in range(deck_width):
                for cy in range(deck_length):
                    grown = [p for ew, eh, x0, y0, p in placements[i]
                             if x0 - gap <= cx < x0 + ew + gap and y0 - gap <= cy < y0 + eh + gap]
                    cover = [p for ew, eh, x0, y0, p in placements[j]
                             if x0 <= cx < x0 + ew and y0 <= cy < y0 + eh]
                    if grown and cover:
                        model.add_constr(mip.xsum(grown) + mip.xsum(cover) <= 1, name=f"sep_{i}_{j}_{cx}_{cy}")

    # The edges of each container follow from the place it takes. right and top are the far edges,
    # just past the last cell the container covers.
    left = []    # left[i]: the left edge of container i across the deck
    right = []   # right[i]: the far edge of container i across the deck
    top = []     # top[i]: the far edge of container i along the deck
    bottom = []  # bottom[i]: the bottom edge of container i along the deck
    for i in range(n_containers):
        lv = model.add_var(name=f"left_{i}", lb=0, ub=deck_width, var_type=mip.INTEGER)
        rv = model.add_var(name=f"right_{i}", lb=0, ub=deck_width, var_type=mip.INTEGER)
        tv = model.add_var(name=f"top_{i}", lb=0, ub=deck_length, var_type=mip.INTEGER)
        bv = model.add_var(name=f"bottom_{i}", lb=0, ub=deck_length, var_type=mip.INTEGER)
        model.add_constr(lv == mip.xsum([x0 * p for ew, eh, x0, y0, p in placements[i]]), name=f"left_def_{i}")
        model.add_constr(rv == mip.xsum([(x0 + ew) * p for ew, eh, x0, y0, p in placements[i]]), name=f"right_def_{i}")
        model.add_constr(bv == mip.xsum([y0 * p for ew, eh, x0, y0, p in placements[i]]), name=f"bottom_def_{i}")
        model.add_constr(tv == mip.xsum([(y0 + eh) * p for ew, eh, x0, y0, p in placements[i]]), name=f"top_def_{i}")
        left.append(lv)
        right.append(rv)
        top.append(tv)
        bottom.append(bv)

    return model, {"left": left, "right": right, "top": top, "bottom": bottom}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
