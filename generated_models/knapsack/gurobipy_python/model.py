# knapsack: a Gurobi (Python) model from DCP Rosetta.
# Download the `knapsack.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/knapsack.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python knapsack.py knapsack.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """A hiker chooses which items to pack: as much total value as possible,
    without the items weighing more than the backpack can carry."""
    values = instance["values"]      # values[i]: the value of item i
    weights = instance["weights"]    # weights[i]: the weight of item i
    capacity = instance["capacity"]  # the most weight the backpack can carry

    model = gp.Model("knapsack")

    # x[i] is 1 when the hiker packs item i, and 0 when not.
    x = [model.addVar(vtype=GRB.BINARY, name=f"x[{i}]") for i in range(len(values))]

    # The packed items weigh no more than the backpack can carry.
    model.addConstr(gp.quicksum(w * xi for w, xi in zip(weights, x)) <= capacity, name="capacity")

    # Pack the most valuable selection: maximise the total value of the packed items.
    model.setObjective(gp.quicksum(v * xi for v, xi in zip(values, x)), GRB.MAXIMIZE)

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
