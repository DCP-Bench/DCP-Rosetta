# netasgn: a Gurobi (Python) model from DCP Rosetta.
# Download the `netasgn.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/netasgn.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python netasgn.py netasgn.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Project assignment: split each person's hours over the projects so that every person works all their hours and every project gets all its hours, at the least total cost."""
    supply = instance["supply"]  # supply[i]: the hours person i has available
    demand = instance["demand"]  # demand[j]: the hours project j requires
    cost = instance["cost"]      # cost[i][j]: the hourly cost of person i on project j
    limit = instance["limit"]    # limit[i][j]: the most hours person i may work on project j
    people = range(len(supply))
    projects = range(len(demand))

    model = gp.Model("netasgn")

    # assign[i, j] is the hours person i works on project j, between 0 and limit[i][j]
    ub = {(i, j): limit[i][j] for i in people for j in projects}
    assign = model.addVars(people, projects, lb=0, ub=ub, vtype=GRB.INTEGER, name="assign")

    # Each person works exactly their available hours.
    model.addConstrs((assign.sum(i, "*") == supply[i] for i in people), name="supply")
    # Each project receives exactly the hours it requires.
    model.addConstrs((assign.sum("*", j) == demand[j] for j in projects), name="demand")

    # Minimise the total cost: each hour assigned costs the hourly cost of that person on that project.
    total_cost = gp.quicksum(cost[i][j] * assign[i, j] for i in people for j in projects)
    model.setObjective(total_cost, GRB.MINIMIZE)

    return model, {"assign": [[assign[i, j] for j in projects] for i in people],
                   "total_cost": total_cost}


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
