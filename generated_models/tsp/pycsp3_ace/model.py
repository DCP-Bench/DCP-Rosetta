# tsp: a PyCSP3 model from DCP Rosetta.
# Download the `tsp.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/tsp.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python tsp.py tsp.json

from pycsp3 import *


def create_model(instance):
    """Find the shortest route that visits each city exactly once and returns to the
    origin city, where the distance between two cities is the Euclidean distance between
    their points rounded to an integer."""
    locations = instance["locations"]  # locations[i] is the [x, y] position of city i
    n_cities = len(locations)

    # dist[i][j] is the distance from city i to city j, rounded to the nearest integer
    # (the Euclidean distance of integer points is never exactly halfway, so round() is unambiguous)
    dist = [[round(((x_i - x_j) ** 2 + (y_i - y_j) ** 2) ** 0.5) for x_j, y_j in locations]
            for x_i, y_i in locations]

    # Each leg of a route is one of the distances in dist, so none exceeds the longest one.
    longest_leg = max(max(row) for row in dist)

    # successor[i] is the city visited right after city i (cities are numbered from 0)
    successor = VarArray(size=n_cities, dom=range(n_cities))

    # legs[i] is the distance of the leg from city i to its successor
    legs = VarArray(size=n_cities, dom=range(longest_leg + 1))

    # travel_distance is the length of the whole route: a route has n_cities legs, each at most longest_leg
    travel_distance = Var(dom=range(n_cities * longest_leg + 1))

    satisfy(
        # The successors form one circuit through all cities, so each city is visited exactly once.
        Circuit(successor),
        # The leg from city i to its successor has the distance between those two cities. A city is never its own
        # successor, so every city is visited: ACE's Circuit also accepts a successor equal to the city itself,
        # which skips the city, so j == i is left out of the supports.
        [Table(scope=[successor[i], legs[i]], supports=[(j, dist[i][j]) for j in range(n_cities) if j != i])
         for i in range(n_cities)],
        # The travel distance is the sum of the legs.
        travel_distance == Sum(legs),
    )

    # The route is as short as possible.
    minimize(travel_distance)

    return {"travel_distance": travel_distance}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is OPTIMUM:
        for name, variable in outputs.items():
            print(name, "=", value(variable))
    else:
        print("No solution:", status())
