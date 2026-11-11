# car_selection: a Gurobi (Python) model from DCP Rosetta.
# Download the `car_selection.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/car_selection.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python car_selection.py car_selection.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Pair participants with the cars they are interested in, so that each participant gets at most one car, each car goes to at most one participant, and as many participants as possible get a car."""
    interested = instance["possible_assignments"]  # possible_assignments[i][j] is 1 if participant i is interested in car j
    participants = range(len(interested))
    cars = range(len(interested[0]))

    model = gp.Model("car_selection")

    # assign[i, j] is 1 when participant i gets car j. A car the participant is
    # not interested in gets an upper bound of 0, so it can never be assigned.
    assign = model.addVars(participants, cars, vtype=GRB.BINARY, name="assign")
    for i in participants:
        for j in cars:
            assign[i, j].UB = interested[i][j]

    # Each participant is assigned to at most one car.
    model.addConstrs((assign.sum(i, "*") <= 1 for i in participants), name="participant")

    # Each car is assigned to at most one participant.
    model.addConstrs((assign.sum("*", j) <= 1 for j in cars), name="car")

    # Maximise the number of assignments.
    model.setObjective(assign.sum(), GRB.MAXIMIZE)

    return model, {"assignments": [[assign[i, j] for j in cars] for i in participants]}


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
