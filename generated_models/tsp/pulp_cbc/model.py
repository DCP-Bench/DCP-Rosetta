# tsp: a PuLP (Python) model from DCP Rosetta.
# Download the `tsp.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/tsp.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python tsp.py tsp.json

import math

import pulp


def create_model(instance):
    """Find the shortest route that visits every city exactly once and returns to the
    city it started from. The distance between two cities is their Euclidean distance
    rounded to an integer."""
    locations = instance["locations"]  # locations[i]: the (x, y) position of city i
    n_cities = len(locations)

    # distance[i][j]: the distance between city i and city j, rounded to an integer
    distance = [[int(round(math.hypot(locations[i][0] - locations[j][0],
                                      locations[i][1] - locations[j][1])))
                 for j in range(n_cities)] for i in range(n_cities)]

    problem = pulp.LpProblem("tsp", pulp.LpMinimize)

    # Every ordered pair of different cities is a possible leg of the route.
    pairs = [(i, j) for i in range(n_cities) for j in range(n_cities) if i != j]

    # leg[i, j] is true when the route goes directly from city i to city j.
    leg = {(i, j): pulp.LpVariable(f"leg_{i}_{j}", cat="Binary") for i, j in pairs}

    # Each city is left once and entered once.
    for i in range(n_cities):
        problem += pulp.lpSum(leg[(i, j)] for j in range(n_cities) if j != i) == 1
        problem += pulp.lpSum(leg[(j, i)] for j in range(n_cities) if j != i) == 1

    # The legs must form one loop through all the cities, not several smaller loops.
    # City 0 sends out n_cities - 1 units of load along the legs of the route, and every
    # other city keeps one unit and passes the rest on. A group of cities that forms a loop
    # without city 0 could never receive load, so such a loop is ruled out.
    # load[i, j] is the load carried on the leg from city i to city j; no load comes into city 0.
    load = {(i, j): pulp.LpVariable(f"load_{i}_{j}", 0, n_cities - 1 if i == 0 else n_cities - 2)
            for i, j in pairs if j != 0}

    # City 0 sends out all of the load.
    problem += pulp.lpSum(load[(0, j)] for j in range(1, n_cities)) == n_cities - 1

    # Each other city keeps one unit: the load coming in exceeds the load going out by one.
    for i in range(1, n_cities):
        problem += (pulp.lpSum(load[(j, i)] for j in range(n_cities) if j != i)
                    - pulp.lpSum(load[(i, j)] for j in range(1, n_cities) if j != i)) == 1

    # Load moves only along legs of the route. A leg of the route carries at least the one
    # unit that its arrival city keeps.
    for (i, j), f in load.items():
        problem += f <= f.upBound * leg[(i, j)]
        problem += f >= leg[(i, j)]

    # With three or more cities, the route never goes between two cities and straight back.
    if n_cities > 2:
        for i in range(n_cities):
            for j in range(i + 1, n_cities):
                problem += leg[(i, j)] + leg[(j, i)] <= 1

    # The same loop can be driven in either direction at the same length. Only the direction
    # whose first city after city 0 has a smaller index than its last city before city 0 is kept.
    if n_cities > 2:
        problem += (pulp.lpSum(j * leg[(0, j)] for j in range(1, n_cities))
                    <= pulp.lpSum(j * leg[(j, 0)] for j in range(1, n_cities)))

    # Each city leaves along one leg, so the longest leg out of each city bounds the route length.
    longest = sum(max(distance[i][j] for j in range(n_cities) if j != i) for i in range(n_cities))

    # travel_distance is the length of the route.
    travel_distance = pulp.LpVariable("travel_distance", 0, longest, cat="Integer")

    # The route length is the sum of the distances of the legs it uses.
    problem += travel_distance == pulp.lpSum(distance[i][j] * leg[(i, j)] for i, j in pairs)

    # The objective: the length of the route, as short as possible.
    problem += travel_distance

    return problem, {"travel_distance": travel_distance}


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
