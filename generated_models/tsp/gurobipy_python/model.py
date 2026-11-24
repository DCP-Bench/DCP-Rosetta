# tsp: a Gurobi (Python) model from DCP Rosetta.
# Download the `tsp.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/tsp.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python tsp.py tsp.json

import math

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Travelling salesman: the shortest round trip that visits every city exactly once and returns
    to the city it started from."""
    locations = instance["locations"]  # locations[i] is the [x, y] position of city i
    n = len(locations)  # the number of cities
    cities = range(n)  # city 0 is the origin where the trip starts and ends

    # dist[i][j] is the Euclidean distance between cities i and j, rounded to an integer (as the statement defines it).
    dist = [[round(math.dist(a, b)) for b in locations] for a in locations]

    model = gp.Model("tsp")

    # arc[i, j] is 1 when the trip goes directly from city i to city j.
    arcs = [(i, j) for i in cities for j in cities if i != j]
    arc = model.addVars(arcs, vtype=GRB.BINARY, name="arc")

    # Each city is left exactly once and entered exactly once.
    model.addConstrs((arc.sum(i, "*") == 1 for i in cities), name="leave")
    model.addConstrs((arc.sum("*", i) == 1 for i in cities), name="enter")

    # The trip must be one round trip, not several loops. position[i] is the place of city i on the trip
    # (city 0 is place 0), and it rises by at least one along each leg that does not return to city 0.
    # These are the Miller-Tucker-Zemlin subtour-elimination constraints: not in the statement, but they
    # rule out loops that miss city 0. The upper bound n - 1 is the last place, chosen to keep the
    # places finite; it is not in the statement.
    position = model.addVars(cities, lb=0, ub=n - 1, vtype=GRB.CONTINUOUS, name="position")
    model.addConstr(position[0] == 0, name="origin")
    model.addConstrs((position[j] >= position[i] + 1 - n * (1 - arc[i, j])
                      for (i, j) in arcs if j != 0), name="order")

    # travel_distance is the length of the trip: the distances of the legs taken, summed. It is minimised.
    # Its upper bound is the sum of the longest leg out of each city, taken from the data (not in the statement).
    travel_distance = model.addVar(lb=0, ub=sum(max(row) for row in dist), vtype=GRB.INTEGER,
                                   name="travel_distance")
    model.addConstr(travel_distance == gp.quicksum(dist[i][j] * arc[i, j] for (i, j) in arcs),
                    name="distance")
    model.setObjective(travel_distance, GRB.MINIMIZE)

    return model, {"travel_distance": travel_distance}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.Params.OutputFlag = 0  # no solver log
    model.Params.MIPGap = 0  # prove the optimum; the default stops within 0.01% of it
    model.optimize()

    if model.Status == GRB.OPTIMAL:  # a proven optimum
        print("Objective value:", round(model.ObjVal))
        # a variable's value is var.X, an expression's is expr.getValue(); both read through LinExpr
        value = np.vectorize(lambda out: round(gp.LinExpr(out).getValue()))
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution, Gurobi status", model.Status)  # 3 infeasible, 4 infeasible or unbounded
