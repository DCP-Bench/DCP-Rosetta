# cabling: a Gurobi (Python) model from DCP Rosetta.
# Download the `cabling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cabling.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python cabling.py cabling.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Cabling: place n devices in the n positions of a rack so that the cables joining them are as short as possible in total."""
    n = instance["n"]                        # the number of devices, and of positions in the rack
    devices = instance["devices"]            # devices[d]: the name of device d
    cable_struct = instance["cable_struct"]  # cable_struct[k] = [a, b, num]: num cables join devices a and b (named)
    positions = range(n)                     # the rack positions, 0 to n - 1

    model = gp.Model("cabling")

    # Devices are numbered by their place in the devices list, so a cable can name its ends by number.
    device_index = {name: d for d, name in enumerate(devices)}
    cables = [(device_index[a], device_index[b], num) for a, b, num in cable_struct]

    # put[d, p] is 1 when device d stands in rack position p.
    put = model.addVars(positions, positions, vtype=GRB.BINARY, name="put")
    # Each device stands in exactly one position.
    model.addConstrs((put.sum(d, "*") == 1 for d in positions), name="one_position")
    # Each position holds exactly one device.
    model.addConstrs((put.sum("*", p) == 1 for p in positions), name="one_device")
    # x[d] is the position of device d.
    x = [gp.quicksum(p * put[d, p] for p in positions) for d in positions]

    # The distance between two devices is the difference of their positions. gp.abs_ takes
    # a variable, so the signed difference of each cable's two ends gets one first.
    signed = model.addVars(len(cables), lb=-(n - 1), ub=n - 1, vtype=GRB.INTEGER, name="signed")
    distance = model.addVars(len(cables), lb=0, ub=n - 1, vtype=GRB.INTEGER, name="distance")
    # signed[k] is the position of one end of cable group k minus the position of the other end.
    model.addConstrs((signed[k] == x[a] - x[b] for k, (a, b, _) in enumerate(cables)), name="signed")
    # distance[k] is the length of one cable of group k: the absolute value of signed[k].
    model.addConstrs((distance[k] == gp.abs_(signed[k]) for k in range(len(cables))), name="distance")

    # Objective: the total length of all the cables, each cable group's length counted once per cable.
    final_sum = gp.quicksum(num * distance[k] for k, (_, _, num) in enumerate(cables))
    model.setObjective(final_sum, GRB.MINIMIZE)

    return model, {"final_sum": final_sum}


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
