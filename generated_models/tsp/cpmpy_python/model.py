# tsp: a CPMpy model from DCP Rosetta.
# Download the `tsp.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/tsp.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python tsp.py tsp.json

import math

import cpmpy as cp
import numpy as np


def create_model(instance):
    """Find the shortest route that visits every city exactly once and returns to the
    starting city; the distance between two cities is their Euclidean distance rounded
    to an integer."""
    locations = instance["locations"]  # locations[i]: the (x, y) coordinates of city i
    n = len(locations)                           # the number of cities

    # dist[i, j] is the Euclidean distance between city i and city j, rounded to an integer
    dist = np.array([[round(math.dist(a, b)) for b in locations] for a in locations])

    # nxt[i] = j means the route goes from city i directly to city j
    nxt = cp.intvar(0, n - 1, shape=n, name="nxt")

    # travel_distance is the length of the whole route. Upper bound: every city leaves
    # along its longest arc.
    travel_distance = cp.intvar(0, int(dist.max(axis=1).sum()), name="travel_distance")

    model = cp.Model()

    # The route is one single circuit through all the cities.
    model.add(cp.Circuit(nxt))

    # The route length is the sum of the distances of the arcs used. Encoding choice: summing
    # arc indicators (nxt[i] == j) times the distance gives the solver a better bound than
    # looking the distance up with a variable index, dist[i][nxt[i]].
    model.add(travel_distance == cp.sum([dist[i, j] * (nxt[i] == j)
                                        for i in range(n) for j in range(n) if i != j]))

    # Minimise the length of the route.
    model.minimize(travel_distance)

    return model, {"travel_distance": travel_distance}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
