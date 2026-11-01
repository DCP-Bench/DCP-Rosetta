# tsp: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `tsp.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/tsp.html
# Then run it on the first instance (after `pip install ortools`):
#   python tsp.py tsp.json

import math

from ortools.sat.python import cp_model


def create_model(instance):
    """Find the shortest route that visits every city exactly once and returns to the
    starting city. The distance between two cities is their Euclidean distance rounded
    to an integer."""
    locations = instance["locations"]  # locations[i]: the (x, y) coordinates of city i
    n_cities = len(locations)          # the number of cities

    # dist[i][j]: the distance between city i and city j
    dist = [[int(round(math.dist(a, b))) for b in locations] for a in locations]

    model = cp_model.CpModel()

    # go[(i, j)] is true when the route goes directly from city i to city j
    go = {(i, j): model.new_bool_var(f"go_{i}_{j}") for i in range(n_cities) for j in range(n_cities) if i != j}
    # The arcs taken form a circuit through all the cities.
    model.add_circuit([(i, j, lit) for (i, j), lit in go.items()])

    # travel_distance is the length of the route.
    travel_distance = model.new_int_var(0, sum(max(row) for row in dist), "travel_distance")
    # The route length is the sum of the distances of the arcs taken.
    model.add(travel_distance == sum(dist[i][j] * lit for (i, j), lit in go.items()))

    # Minimise the length of the route.
    model.minimize(travel_distance)

    return model, {"travel_distance": travel_distance}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
