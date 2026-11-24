# aircraft_landing: a Gurobi (Python) model from DCP Rosetta.
# Download the `aircraft_landing.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/aircraft_landing.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python aircraft_landing.py aircraft_landing.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Give each aircraft on a single runway a landing time inside its time window, keeping the fixed landing order and the separation times, so that the total penalty for landing before or after the target times is as small as possible."""
    earliest = instance["earliest_landing"]  # earliest[i]: the earliest time aircraft i can land
    latest = instance["latest_landing"]  # latest[i]: the latest time aircraft i can land
    target = instance["target_landing"]  # target[i]: the time aircraft i should land
    penalty_after = instance["penalty_after"]  # penalty_after[i]: cost per unit of time aircraft i lands after its target
    penalty_before = instance["penalty_before"]  # penalty_before[i]: cost per unit of time aircraft i lands before its target
    separation = instance["separation_time"]  # separation[i][j]: minimum time between the landings of aircraft i and j
    planes = range(len(earliest))  # the aircraft, numbered from 0, in their fixed landing order
    horizon = max(latest)  # upper bound on times, earliness and lateness: the largest latest landing time (not in the statement; the reference model's bound)

    model = gp.Model("aircraft_landing")

    # landing[i] is the time at which aircraft i lands
    landing = model.addVars(planes, lb=0, ub=horizon, vtype=GRB.INTEGER, name="landing")
    # earliness[i] is the number of time units aircraft i lands before its target
    earliness = model.addVars(planes, lb=0, ub=horizon, vtype=GRB.INTEGER, name="earliness")
    # lateness[i] is the number of time units aircraft i lands after its target
    lateness = model.addVars(planes, lb=0, ub=horizon, vtype=GRB.INTEGER, name="lateness")

    # Each aircraft lands inside its time window: no earlier than its earliest time, no later than its latest.
    model.addConstrs((landing[i] >= earliest[i] for i in planes), name="earliest")
    model.addConstrs((landing[i] <= latest[i] for i in planes), name="latest")

    # The landing time is the target time plus the lateness, minus the earliness.
    model.addConstrs((landing[i] - target[i] == lateness[i] - earliness[i] for i in planes), name="target")

    # The landing sequence is fixed: aircraft i lands before aircraft j when i < j,
    # and the second lands at least separation[i][j] time units after the first.
    model.addConstrs((landing[j] - landing[i] >= separation[i][j]
                      for i in planes for j in planes if j > i), name="separation")

    # The objective: the total penalty, earliness at penalty_before per unit and lateness at
    # penalty_after per unit, summed over all aircraft, is minimised.
    total_penalty = gp.quicksum(penalty_before[i] * earliness[i] + penalty_after[i] * lateness[i] for i in planes)
    model.setObjective(total_penalty, GRB.MINIMIZE)

    # outputs: the landing time of each aircraft, and the total penalty
    return model, {"landing_times": [landing[i] for i in planes], "total_penalty": total_penalty}


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
