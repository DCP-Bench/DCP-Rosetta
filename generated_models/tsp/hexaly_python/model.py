"""Travelling salesman: the shortest tour through all locations, with distances rounded to integers."""
from math import hypot

import hexaly.optimizer as hx


def build(instance):
    locations = instance["locations"]  # locations[i] = the (x, y) coordinates of location i
    n = len(locations)  # number of locations
    # dist[i][j] = the distance between locations i and j: the Euclidean distance rounded to an integer
    dist = [[int(round(hypot(a[0] - b[0], a[1] - b[1]))) for b in locations] for a in locations]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # arc[i][j] = 1 if the tour goes from location i directly to location j (the constant 0 on the
    # diagonal: no arc from a location to itself). Boolean arcs with degree constraints and an ordering
    # against sub-tours are linear, the form Hexaly proves a shortest tour on.
    arc = [[model.bool() if i != j else 0 for j in range(n)] for i in range(n)]
    for i in range(n):
        # Every location is visited once: it is left by one arc and entered by one arc
        model.constraint(model.sum(arc[i][j] for j in range(n) if j != i) == 1)
        model.constraint(model.sum(arc[j][i] for j in range(n) if j != i) == 1)
    # order[i] = position of location i on the tour, 0 at location 0.
    # No separate loops: the position increases along every arc except those back into location 0,
    # which close the tour. n serves as the big-M, since positions lie between 0 and n - 1, so the
    # constraint is slack for an arc that is not used.
    order = [model.int(0, n - 1) for _ in range(n)]
    model.constraint(order[0] == 0)
    for i in range(n):
        for j in range(1, n):
            if i != j:
                model.constraint(order[j] >= order[i] + 1 - n * (1 - arc[i][j]))

    # Minimise the length of the tour: the total distance of the arcs it uses
    travel_distance = model.sum(dist[i][j] * arc[i][j] for i in range(n) for j in range(n) if i != j)
    model.minimize(travel_distance)
    return optimizer, {"travel_distance": travel_distance}
