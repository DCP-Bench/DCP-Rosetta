# csplib_016_traffic_lights: a Gurobi (Python) model from DCP Rosetta.
# Download the `csplib_016_traffic_lights.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_016_traffic_lights.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python csplib_016_traffic_lights.py csplib_016_traffic_lights.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Traffic lights: set the eight lights of a four-way junction so that every pair of neighbouring
    roads shows one of the light combinations that are safe for crossing roads."""
    allowed = instance["allowed_tuples"]  # allowed[k] is (V_i, P_i, V_{i+1}, P_{i+1}), a safe combination
    roads = range(4)  # the four roads of the junction
    tuples = range(len(allowed))  # the safe combinations, numbered

    model = gp.Model("traffic_lights")

    # The light states from the statement: a vehicle light is 0 red, 1 red-yellow, 2 green or
    # 3 yellow; a pedestrian light is 0 red or 1 green.
    # vehicle[i] is the state of the vehicle light V_{i+1}; pedestrian[i] that of the pedestrian light P_{i+1}.
    vehicle = [model.addVar(lb=0, ub=3, vtype=GRB.INTEGER, name=f"V{i + 1}") for i in roads]
    pedestrian = [model.addVar(vtype=GRB.BINARY, name=f"P{i + 1}") for i in roads]

    # pick[i, k] is 1 when road i and the next road (road 4 is followed by road 1) show the k-th safe combination.
    pick = model.addVars(roads, tuples, vtype=GRB.BINARY, name="pick")
    # Each pair of neighbouring roads shows exactly one safe combination.
    model.addConstrs((pick.sum(i, "*") == 1 for i in roads), name="one_tuple")

    # corner[i] lists the four lights of road i and the next road, in the order of a safe combination.
    corner = [[vehicle[i], pedestrian[i], vehicle[(i + 1) % 4], pedestrian[(i + 1) % 4]] for i in roads]
    # The four lights of the pair take the values of the combination picked for that pair.
    model.addConstrs((corner[i][p] == gp.quicksum(allowed[k][p] * pick[i, k] for k in tuples)
                      for i in roads for p in range(4)), name="table")

    return model, {"lights": vehicle + pedestrian}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.Params.OutputFlag = 0  # no solver log
    model.optimize()

    if model.Status == GRB.OPTIMAL:  # a solution
        # a variable's value is var.X, an expression's is expr.getValue(); both read through LinExpr
        value = np.vectorize(lambda out: round(gp.LinExpr(out).getValue()))
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution, Gurobi status", model.Status)  # 3 infeasible, 4 infeasible or unbounded
