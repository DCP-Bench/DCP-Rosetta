# tsp: an Exact (Python) model from DCP Rosetta.
# Download the `tsp.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/tsp.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python tsp.py tsp.json

import math
from itertools import combinations

from exact import Exact


def create_model(instance):
    """Find the shortest tour that visits every city exactly once and returns to the
    starting city. The distance between two cities is their Euclidean distance rounded
    to an integer."""
    locations = instance["locations"]  # locations[i]: the (x, y) coordinates of city i
    n_cities = len(locations)          # the number of cities

    # distance[i][j]: the distance between city i and city j
    distance = [[0 if i == j else int(round(math.hypot(locations[i][0] - locations[j][0],
                                                       locations[i][1] - locations[j][1])))
                 for j in range(n_cities)] for i in range(n_cities)]

    # A tour from city 0 that always goes to the nearest unvisited city. Stretches of it are
    # reversed while a reversal shortens it.
    tour = [0]
    while len(tour) < n_cities:
        last = tour[-1]
        tour.append(min((c for c in range(n_cities) if c not in tour), key=lambda c: distance[last][c]))
    improved = n_cities > 3
    while improved:
        improved = False
        for a in range(1, n_cities - 1):
            for b in range(a + 1, n_cities):
                before = distance[tour[a - 1]][tour[a]] + distance[tour[b]][tour[(b + 1) % n_cities]]
                after = distance[tour[a - 1]][tour[b]] + distance[tour[a]][tour[(b + 1) % n_cities]]
                if after < before:
                    tour[a:b + 1] = reversed(tour[a:b + 1])
                    improved = True
    # Length of that tour. The shortest tour is no longer than this.
    upper = sum(distance[tour[k]][tour[(k + 1) % n_cities]] for k in range(n_cities))

    # Every city is left by one arc, so the tour is at least the sum over the cities of the
    # shortest arc leaving each city.
    lower = sum(min(distance[i][j] for j in range(n_cities) if j != i)
                for i in range(n_cities)) if n_cities > 1 else 0

    solver = Exact()

    # Exact identifies its variables by name.
    # go[i][j] is 1 when the tour goes directly from city i to city j, and 0 when not
    go = [[f"go_{i}_{j}" if i != j else None for j in range(n_cities)] for i in range(n_cities)]
    for i in range(n_cities):
        for j in range(n_cities):
            if i != j:
                solver.addVariable(go[i][j], 0, 1)

    # Each city is left by exactly one arc and entered by exactly one arc.
    for i in range(n_cities):
        solver.addConstraint([(1, go[i][j]) for j in range(n_cities) if j != i],
                             True, 1, True, 1)
        solver.addConstraint([(1, go[j][i]) for j in range(n_cities) if j != i],
                             True, 1, True, 1)

    # order[i] is the position of city i on the tour, from 1 to n-1. The start city 0 has no position.
    order = [None] + [f"order_{i}" for i in range(1, n_cities)]
    for i in range(1, n_cities):
        solver.addVariable(order[i], 1, n_cities - 1)
    if n_cities > 2:
        # The tour is one loop through all the cities. An arc from city i to city j, neither of
        # them the start, puts city j later in the order than city i, so no loop avoids the start.
        for i in range(1, n_cities):
            for j in range(1, n_cities):
                if i != j:
                    terms = [(1, order[i]), (-1, order[j]), (n_cities - 1, go[i][j])]
                    if n_cities > 3:
                        terms.append((n_cities - 3, go[j][i]))
                    solver.addConstraint(terms, False, 0, True, n_cities - 2)
        # The tour never goes from one city to another and straight back.
        for i, j in combinations(range(n_cities), 2):
            solver.addConstraint([(1, go[i][j]), (1, go[j][i])], False, 0, True, 1)
    if n_cities > 3:
        # The tour does not close a loop through three cities: at most two arcs are used among
        # any three cities.
        for i, j, k in combinations(range(n_cities), 3):
            solver.addConstraint([(1, go[a][b]) for a in (i, j, k) for b in (i, j, k) if a != b],
                                 False, 0, True, 2)
    if n_cities > 4:
        # The same for four cities: at most three arcs are used among any four cities.
        for group in combinations(range(n_cities), 4):
            solver.addConstraint([(1, go[a][b]) for a in group for b in group if a != b],
                                 False, 0, True, 3)

    # travel_distance is the length of the tour: the sum of the distances of the arcs used.
    solver.addVariable("travel_distance", 0, upper)
    solver.addConstraint([(distance[i][j], go[i][j]) for i in range(n_cities)
                          for j in range(n_cities) if i != j and distance[i][j]]
                         + [(-1, "travel_distance")], True, 0, True, 0)
    solver.addConstraint([(1, "travel_distance")], True, lower)

    # Find the shortest tour.
    solver.setObjective([(1, "travel_distance")], minimize=True)

    return solver, {"travel_distance": "travel_distance"}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
