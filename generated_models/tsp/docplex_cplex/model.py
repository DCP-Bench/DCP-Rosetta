# tsp: a CPLEX (Python) model from DCP Rosetta.
# Download the `tsp.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/tsp.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python tsp.py tsp.json

import math
from docplex.mp.model import Model


def create_model(instance):
    """Travelling salesman: find the shortest round trip that visits every city exactly once and returns
    to its start, with distances the Euclidean distances between the cities rounded to integers."""
    locations = instance["locations"]  # locations[i]: the (x, y) coordinates of city i
    n = len(locations)  # the number of cities
    cities = range(n)

    # dist[i][j]: the Euclidean distance between cities i and j, rounded to an integer.
    dist = [[round(math.hypot(a[0] - b[0], a[1] - b[1])) for b in locations] for a in locations]

    model = Model("tsp")

    # nxt[i, j] = 1 when city j is visited immediately after city i.
    arcs = [(i, j) for i in cities for j in cities if i != j]
    nxt = {(i, j): model.binary_var(name=f"next_{i}_{j}") for (i, j) in arcs}

    # Every city is left once and entered once.
    model.add_constraints(model.sum(nxt[i, j] for j in cities if j != i) == 1 for i in cities)
    model.add_constraints(model.sum(nxt[j, i] for j in cities if j != i) == 1 for i in cities)

    # The trip is a single circuit: order[i] is the position of city i on the trip counted
    # from city 0, and it grows by one along every arc not returning to city 0 (Miller-Tucker-
    # Zemlin constraints, lifted by Desrochers and Laporte). This needs one constraint per arc,
    # which keeps 30 cities inside the Community Edition's 1000 variables and constraints.
    if n > 2:  # with at most two cities the arcs taken already form a single circuit
        order = {i: model.integer_var(1, n - 1, name=f"order_{i}") for i in cities if i != 0}
        model.add_constraints(order[i] - order[j] + (n - 1) * nxt[i, j] + (n - 3) * nxt[j, i] <= n - 2
                              for i in order for j in order if i != j)

    # The travel distance is the sum of the distances of the arcs taken; minimize it.
    travel_distance = model.sum(dist[i][j] * nxt[i, j] for (i, j) in arcs)
    model.minimize(travel_distance)

    return model, {"travel_distance": travel_distance}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.parameters.mip.tolerances.mipgap = 0  # prove the optimum; the default stops within 0.01% of it
    solution = model.solve()

    if solution:  # a proven optimum
        print("Objective value:", round(solution.objective_value))

        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
