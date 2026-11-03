"""Travelling salesman: the shortest tour through all locations, with distances rounded to integers."""
from math import hypot

import hexaly.optimizer as hx


def build(instance):
    locations = instance["locations"]
    n = len(locations)
    # The distance between two locations is the Euclidean distance rounded to an integer
    dist = [[int(round(hypot(a[0] - b[0], a[1] - b[1]))) for b in locations] for a in locations]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # arc[i][j] = 1 if the tour goes from location i directly to location j. Boolean arcs with
    # degree constraints and an ordering against sub-tours give Hexaly bounds a permutation does not.
    arc = [[model.bool() if i != j else 0 for j in range(n)] for i in range(n)]
    for i in range(n):
        # Every location is left once and entered once
        model.constraint(model.sum(arc[i][j] for j in range(n) if j != i) == 1)
        model.constraint(model.sum(arc[j][i] for j in range(n) if j != i) == 1)
    # No separate loops: location 0 comes first and the order increases along every arc leading
    # away from it round to the last location
    order = [model.int(0, n - 1) for _ in range(n)]
    model.constraint(order[0] == 0)
    for i in range(n):
        for j in range(1, n):
            if i != j:
                model.constraint(order[j] >= order[i] + 1 - n * (1 - arc[i][j]))

    # Minimise the length of the tour
    travel_distance = model.sum(dist[i][j] * arc[i][j] for i in range(n) for j in range(n) if i != j)
    model.minimize(travel_distance)
    return optimizer, {"travel_distance": travel_distance}
