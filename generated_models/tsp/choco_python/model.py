# tsp: a Choco-solver (Python) model from DCP Rosetta.
# Download the `tsp.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/tsp.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python tsp.py tsp.json

import math

from pychoco.model import Model


def create_model(instance):
    """Find the shortest route that visits every city exactly once and returns to the
    starting city. The distance between two cities is their straight-line distance,
    rounded to an integer."""
    locations = instance["locations"]  # locations[i]: the (x, y) position of city i
    n_cities = len(locations)          # the number of cities

    # distance[i][j]: the distance between city i and city j
    distance = [[round(math.dist(a, b)) for b in locations] for a in locations]

    model = Model()

    # successor[i] is the city visited right after city i.
    successor = [model.intvar(0, n_cities - 1, name=f"successor_{i}") for i in range(n_cities)]

    # The successors form one round trip through all the cities.
    model.circuit(successor).post()

    # leg[i] is the distance from city i to the city after it on the route, read from row i of the distance table.
    leg = []
    for i in range(n_cities):
        leg.append(model.intvar(min(distance[i]), max(distance[i]), name=f"leg_{i}"))
        model.element(leg[i], distance[i], successor[i]).post()

    # travel_distance is the length of the route, the sum of its legs. It is minimised.
    travel_distance = model.intvar(0, sum(max(row) for row in distance), name="travel_distance")
    model.sum(leg, "=", travel_distance).post()

    return model, {"travel_distance": travel_distance}, {"objective": travel_distance, "maximize": False}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
