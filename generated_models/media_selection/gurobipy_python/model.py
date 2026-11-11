# media_selection: a Gurobi (Python) model from DCP Rosetta.
# Download the `media_selection.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/media_selection.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python media_selection.py media_selection.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Media selection: choose which advertising media to buy so that every target audience is reached at least once, at the least total cost."""
    reaches = instance["incidence_matrix"]  # reaches[t][m] is 1 if medium m reaches audience t
    media_costs = instance["media_costs"]   # media_costs[m]: the cost of medium m
    audiences = range(len(instance["target_audiences"]))  # one index per target audience; only the count is used
    media = range(len(instance["advertising_media"]))     # one index per advertising medium; only the count is used

    model = gp.Model("media_selection")

    # is_selected[m] is 1 when medium m is part of the campaign.
    is_selected = model.addVars(media, vtype=GRB.BINARY, name="is_selected")

    # Every target audience is reached by at least one selected medium.
    model.addConstrs((gp.quicksum(reaches[t][m] * is_selected[m] for m in media) >= 1
                      for t in audiences), name="audience")

    # The total cost of the selected media, to be minimised.
    min_total_cost = gp.quicksum(media_costs[m] * is_selected[m] for m in media)
    model.setObjective(min_total_cost, GRB.MINIMIZE)

    return model, {"is_selected": [is_selected[m] for m in media], "min_total_cost": min_total_cost}


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
