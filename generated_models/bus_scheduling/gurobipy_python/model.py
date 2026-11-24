# bus_scheduling: a Gurobi (Python) model from DCP Rosetta.
# Download the `bus_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bus_scheduling.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python bus_scheduling.py bus_scheduling.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Bus scheduling: the fewest buses that meet the demand of every 4-hour interval of the day, where each bus works 8 successive hours."""
    demands = instance["demands"]  # demands[k]: the number of buses needed in 4-hour interval k
    n = len(demands)               # the day has n intervals; the last one is followed by the first
    intervals = range(n)

    model = gp.Model("bus_scheduling")

    # x[k] is the number of buses that start work in interval k. The upper bound is not in the
    # statement: it is the total demand, chosen to keep each count finite.
    x = model.addVars(intervals, lb=0, ub=sum(demands), vtype=GRB.INTEGER, name="x")

    # A bus works 8 hours, which is two intervals: a bus that starts in interval k covers intervals k
    # and k + 1. So interval k is covered by the buses that start in interval k - 1 and those that
    # start in interval k together, and these must meet its demand. The day wraps around, so the
    # interval before interval 0 is interval n - 1.
    model.addConstrs((x[(k - 1) % n] + x[k] >= demands[k] for k in intervals), name="cover")

    # The objective: the total number of buses, to minimise.
    model.setObjective(x.sum(), GRB.MINIMIZE)

    return model, {"x": [x[k] for k in intervals]}


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
