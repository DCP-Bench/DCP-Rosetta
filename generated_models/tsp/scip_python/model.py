# tsp: a SCIP (Python) model from DCP Rosetta.
# Download the `tsp.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/tsp.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python tsp.py tsp.json

import math

import numpy as np
from pyscipopt import Model


def create_model(instance):
    """The travelling salesperson problem: visit every city exactly once and
    return to the start city, using the shortest possible route. The distance
    between two cities is the Euclidean distance between their points, rounded
    to an integer. The output travel_distance is the length of that shortest
    route."""
    locations = instance["locations"]  # locations[i]: the [x, y] point of city i
    n = len(locations)                 # the number of cities, read from the data

    # dist[i][j]: the distance from city i to city j, rounded to an integer.
    # The square root of an integer is never exactly k + 0.5, so the rounding is unambiguous.
    dist = np.array([[round(math.dist(p, q)) for q in locations] for p in locations])

    model = Model("tsp")

    # x[i, j] is 1 when the route goes straight from city i to city j, and 0 when not.
    # A city does not travel to itself, so the diagonal has upper bound 0.
    x = model.addMatrixVar((n, n), vtype="B", name="x",
                           ub=[[0 if i == j else 1 for j in range(n)] for i in range(n)])

    # pos[i] is the place of city i on the route, counted from the start city 0.
    # The start is at place 0 by its bounds; each of the other n-1 cities is at a place from 1 to n-1.
    pos = [model.addVar(f"pos_{i}", vtype="I", lb=0 if i == 0 else 1,
                        ub=0 if i == 0 else n - 1)
           for i in range(n)]

    # Each city is left exactly once: one arc leaves every city.
    model.addMatrixCons(x.sum(axis=1) == 1)
    # Each city is entered exactly once: one arc enters every city.
    model.addMatrixCons(x.sum(axis=0) == 1)

    # Miller-Tucker-Zemlin constraints: when the route goes straight from city i to city j
    # (with j not the start city, which closes the route), city j comes later on the route
    # than city i. A cycle of cities that does not pass the start would need its places to
    # increase all the way round, which is impossible, so no such cycle survives. This takes
    # one constraint per arc, where one constraint per subset of cities would be exponentially many.
    for i in range(n):
        for j in range(1, n):
            if i != j:
                model.addConsIndicator(pos[j] - pos[i] >= 1, binvar=x[i, j])

    # travel_distance is the length of the route: the distances of the arcs it uses.
    # It is also the objective. The length is held as one bounded integer variable, not only
    # as the sum. Its upper bound: the route has n arcs and no arc is longer than the
    # largest distance in the data.
    travel_distance = model.addVar("travel_distance", vtype="I", lb=0,
                                   ub=n * int(dist.max()))
    model.addCons(travel_distance == (dist * x).sum())
    model.setObjective(travel_distance, "minimize")

    return model, {"travel_distance": travel_distance}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
