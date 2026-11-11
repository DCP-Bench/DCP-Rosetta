# mario: a Gurobi (Python) model from DCP Rosetta.
# Download the `mario.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/mario.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python mario.py mario.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Mario starts at his house and ends at Luigi's house, visiting any houses in between, and the route returns to Mario's house. Choose the route that uses at most the fuel limit and collects the most gold."""
    n = instance["nHouses"]  # the number of houses
    mario = instance["marioHouse"]  # the house where Mario starts
    luigi = instance["luigiHouse"]  # the house where the route ends
    fuel_limit = instance["fuelLimit"]  # the most fuel Mario has
    arc_fuel = instance["arc_fuel"]  # arc_fuel[i][j]: the fuel used travelling from house i to house j
    gold = instance["goldInHouse"]  # gold[i]: the gold in house i
    houses = range(n)

    model = gp.Model("mario")

    # arc[i, j] is 1 when house j succeeds house i on the route. A house off the route is
    # its own successor: arc[i, i] is 1 when house i is not on the route.
    arc = model.addVars(houses, houses, vtype=GRB.BINARY, name="arc")

    # Each house has exactly one successor.
    model.addConstrs((arc.sum(i, "*") == 1 for i in houses), name="succ")
    # Each house has exactly one predecessor, so the successors are all different.
    model.addConstrs((arc.sum("*", j) == 1 for j in houses), name="pred")

    # The route returns from Luigi's house to Mario's house.
    model.addConstr(arc[luigi, mario] == 1, name="luigi_to_mario")

    # Mario starts the route, so his house is on it and is not its own successor.
    # This follows from the statement; it is not an extra rule.
    model.addConstr(arc[mario, mario] == 0, name="mario_on_route")

    # order[i] is the place of house i along the route, from 1 at Mario's house up to n.
    # NOT IN THE STATEMENT: these rank constraints (Miller-Tucker-Zemlin) rule out a cycle
    # that does not pass through Mario's house. Along each used arc into a house other than
    # Mario's, the rank rises by one; when the arc is not used, n makes the constraint slack.
    order = model.addVars(houses, lb=1, ub=n, vtype=GRB.CONTINUOUS, name="order")
    model.addConstr(order[mario] == 1, name="mario_rank")
    model.addConstrs((order[j] >= order[i] + 1 - n * (1 - arc[i, j])
                      for i in houses for j in houses if i != j and j != mario), name="rank")

    # The fuel used on the arcs of the route is at most the fuel Mario has.
    model.addConstr(gp.quicksum(arc_fuel[i][j] * arc[i, j] for i in houses for j in houses) <= fuel_limit,
                    name="fuel")

    # Maximise the gold of the houses on the route. arc[i, i] is 0 for a house on the route,
    # so 1 - arc[i, i] counts that house's gold once.
    model.setObjective(gp.quicksum(gold[i] * (1 - arc[i, i]) for i in houses), GRB.MAXIMIZE)

    # s[i] is the house that follows house i on the route; s[i] = i when house i is off it.
    s = [gp.quicksum(j * arc[i, j] for j in houses) for i in houses]
    return model, {"s": s}


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
