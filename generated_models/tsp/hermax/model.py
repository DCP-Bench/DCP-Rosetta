# tsp: a hermax (Python) model from DCP Rosetta.
# Download the `tsp.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/tsp.html
# Then run it on the first instance (after `pip install hermax`):
#   python tsp.py tsp.json

import math

from hermax.model import Model, sum_expr


def create_model(instance):
    """Find a shortest round trip that starts at the origin city (city 0), visits every
    city exactly once and returns to the origin, where the distance between two cities is
    the Euclidean distance between their points rounded to an integer."""
    locations = instance["locations"]  # locations[i] = [x, y] of city i; city 0 is the origin
    n = len(locations)  # n: the number of cities

    # dist[i][j]: the Euclidean distance from city i to city j, rounded to an integer
    dist = [[round(math.hypot(locations[i][0] - locations[j][0],
                              locations[i][1] - locations[j][1]))
             for j in range(n)] for i in range(n)]

    m = Model()

    # go[i, j] is true when the round trip travels directly from city i to city j
    go = {(i, j): m.bool(f"go_{i}_{j}") for i in range(n) for j in range(n) if i != j}

    # Every city is left exactly once: one trip leaves each city.
    for i in range(n):
        m &= (sum(go[i, j] for j in range(n) if j != i) == 1)

    # Every city is entered exactly once: one trip arrives at each city.
    for j in range(n):
        m &= (sum(go[i, j] for i in range(n) if i != j) == 1)

    # position[i] is the place of city i on the trip after the origin: 1 for the first
    # city visited, up to n - 1 for the last. A trip from city i to city j, neither of them
    # the origin, moves to the next place, so the trip cannot close a loop without the origin.
    position = [None] + [m.int(f"position_{i}", 1, n - 1) for i in range(1, n)]
    for i in range(1, n):
        for j in range(1, n):
            if i != j:
                m &= (position[j] == position[i] + 1).only_if(go[i, j])

    # The first city visited after the origin is in place 1. This fixes the places to the
    # actual visiting order; it is not needed to rule out loops.
    for j in range(1, n):
        m &= (position[j] == 1).only_if(go[0, j])

    # total is the length of the round trip: the sum of the distances of the trips taken.
    # It is the reported travel_distance.
    total = sum_expr(dist[i][j] * lit for (i, j), lit in go.items())

    # Every city is left once and entered once, so every round trip pays the least distance
    # out of each city and then the least remaining distance into each city. Subtracting
    # these from the distances shifts the length of every round trip by the same constant,
    # so the shortest round trip stays the shortest. The plain sum of distances is too slow
    # for hermax's search beyond about 20 cities; the reduced distances are not.
    row_min = [min(dist[i][j] for j in range(n) if j != i) for i in range(n)]
    col_min = [min(dist[i][j] - row_min[i] for i in range(n) if i != j) for j in range(n)]
    reduced = [[dist[i][j] - row_min[i] - col_min[j] for j in range(n)] for i in range(n)]

    # Minimise the total length of the round trip, with the reduced distances. A reduced
    # distance of zero costs nothing, so its trip gets no soft clause.
    m.obj += sum_expr(reduced[i][j] * lit for (i, j), lit in go.items() if reduced[i][j] > 0)

    return m, {"travel_distance": total}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
