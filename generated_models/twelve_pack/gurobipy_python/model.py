# twelve_pack: a Gurobi (Python) model from DCP Rosetta.
# Download the `twelve_pack.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/twelve_pack.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python twelve_pack.py twelve_pack.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Twelve pack: buy packs of the given sizes to get at least the target number of items, with as few items over the target as possible."""
    packs = instance["packs"]  # packs[i]: how many items pack kind i holds
    target = instance["target"]  # the number of items wanted
    kinds = range(len(packs))

    model = gp.Model("twelve_pack")

    # counts[i] is how many packs of kind i are bought.
    counts = model.addVars(kinds, vtype=GRB.INTEGER, name="counts")

    # The items bought meet or exceed the target.
    total = gp.quicksum(packs[i] * counts[i] for i in kinds)  # total: the number of items bought
    model.addConstr(total >= target, name="enough")

    # Objective: buy as few items as possible, which is the closest total that meets or exceeds the target.
    model.setObjective(total, GRB.MINIMIZE)

    return model, {"counts": [counts[i] for i in kinds]}


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
