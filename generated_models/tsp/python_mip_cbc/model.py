# tsp: a Python-MIP (Python) model from DCP Rosetta.
# Download the `tsp.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/tsp.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python tsp.py tsp.json

import math

import mip


def create_model(instance):
    """Find the shortest route that visits every city exactly once and returns to the
    starting city. The distance between two cities is their Euclidean distance rounded
    to an integer."""
    locations = instance["locations"]  # locations[i] is the (x, y) position of city i
    n_cities = len(locations)          # the number of cities

    # dist[i][j] is the distance from city i to city j
    dist = [[int(math.floor(math.hypot(a[0] - b[0], a[1] - b[1]) + 0.5)) for b in locations]
            for a in locations]

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # go[i][j] is 1 when the route travels directly from city i to city j
    go = [[None] * n_cities for _ in range(n_cities)]
    for i in range(n_cities):
        for j in range(n_cities):
            if i != j:
                go[i][j] = model.add_var(f"go_{i}_{j}", var_type=mip.BINARY)

    # The route leaves each city exactly once.
    for i in range(n_cities):
        model.add_constr(mip.xsum(go[i][j] for j in range(n_cities) if j != i) == 1)

    # The route enters each city exactly once.
    for j in range(n_cities):
        model.add_constr(mip.xsum(go[i][j] for i in range(n_cities) if i != j) == 1)

    # The route never goes from one city to another and straight back.
    for i in range(n_cities):
        for j in range(i + 1, n_cities):
            model.add_constr(go[i][j] + go[j][i] <= 1)

    # order[j] is the step at which the route reaches city j, counting from the start city
    # at step 0. The other cities take steps 1 to n_cities - 1.
    order = [0] + [model.add_var(f"order_{j}", lb=1, ub=n_cities - 1, var_type=mip.INTEGER)
                   for j in range(1, n_cities)]

    # Steps increase along the route, so the route cannot close a loop that skips the start city.
    for i in range(n_cities):
        for j in range(1, n_cities):
            if i != j:
                model.add_constr(order[i] - order[j] + (n_cities - 1) * go[i][j]
                                 + (n_cities - 3) * go[j][i] <= n_cities - 2)

    # The length of the route is the total distance of the trips taken. The route should be as short as possible.
    travel_distance = mip.xsum(dist[i][j] * go[i][j]
                               for i in range(n_cities) for j in range(n_cities) if i != j)
    model.objective = travel_distance

    return model, {"travel_distance": travel_distance}


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
