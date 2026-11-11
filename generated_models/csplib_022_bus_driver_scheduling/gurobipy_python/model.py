# csplib_022_bus_driver_scheduling: a Gurobi (Python) model from DCP Rosetta.
# Download the `csplib_022_bus_driver_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_022_bus_driver_scheduling.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python csplib_022_bus_driver_scheduling.py csplib_022_bus_driver_scheduling.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Bus driver scheduling: choose shifts so that every piece of work is covered by exactly one chosen shift, using as few shifts as possible."""
    num_work = instance["num_work"]  # the number of pieces of work
    num_shifts = instance["num_shifts"]  # the number of candidate shifts
    shifts = instance["shifts"]  # shifts[i]: the pieces of work that shift i covers

    model = gp.Model("bus_driver_scheduling")

    # x[i] is 1 when shift i is selected, and 0 when not.
    x = [model.addVar(vtype=GRB.BINARY, name=f"x[{i}]") for i in range(num_shifts)]

    # Each piece of work is covered by exactly one selected shift (a set partition).
    model.addConstrs(
        (gp.quicksum(x[i] for i, covered in enumerate(shifts) if task in covered) == 1
         for task in range(num_work)),
        name="cover",
    )

    # Objective: the number of shifts selected. Every shift costs the same, so fewer shifts is better.
    model.setObjective(gp.quicksum(x), GRB.MINIMIZE)

    return model, {"x": x}


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
