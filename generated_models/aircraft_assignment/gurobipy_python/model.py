# aircraft_assignment: a Gurobi (Python) model from DCP Rosetta.
# Download the `aircraft_assignment.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/aircraft_assignment.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python aircraft_assignment.py aircraft_assignment.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Aircraft assignment: assign aircraft of each type to routes at least cost so that every route's demand is carried."""
    availability = instance["availability"]  # availability[a]: how many aircraft of type a there are
    demand = instance["demand"]              # demand[r]: passengers to carry on route r
    capabilities = instance["capabilities"]  # capabilities[a][r]: passengers one aircraft of type a carries on route r
    costs = instance["costs"]                # costs[a][r]: cost of one aircraft of type a flying route r
    types = range(len(availability))
    routes = range(len(demand))

    model = gp.Model("aircraft_assignment")

    # allocation[a, r] is the number of aircraft of type a flying route r. The upper bound,
    # the largest fleet, is not in the statement: it is taken from the data, to keep the
    # variables finite.
    allocation = model.addVars(types, routes, lb=0, ub=max(availability), vtype=GRB.INTEGER, name="allocation")

    # The aircraft of each type, over all routes, are no more than the number available.
    model.addConstrs((allocation.sum(a, "*") <= availability[a] for a in types), name="fleet")

    # The aircraft on each route carry at least the route's demand.
    model.addConstrs((gp.quicksum(capabilities[a][r] * allocation[a, r] for a in types) >= demand[r]
                      for r in routes), name="demand")

    # Minimise the total cost of the aircraft on their routes.
    model.setObjective(gp.quicksum(costs[a][r] * allocation[a, r] for a in types for r in routes), GRB.MINIMIZE)

    return model, {"allocation": [[allocation[a, r] for r in routes] for a in types]}


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
