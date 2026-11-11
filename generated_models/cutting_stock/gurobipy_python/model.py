# cutting_stock: a Gurobi (Python) model from DCP Rosetta.
# Download the `cutting_stock.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cutting_stock.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python cutting_stock.py cutting_stock.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Cut raw rolls of one width, each cut following one of a fixed set of patterns, so that for each piece width the pieces cut meet the number ordered, using as few raw rolls as possible."""
    pieces = instance["num_rolls_width"]  # pieces[p][w]: pieces of width w that one cut of pattern p yields
    orders = instance["orders"]  # orders[w]: how many pieces of width w are ordered
    patterns = range(instance["num_patterns"])  # the cutting patterns, numbered from 0
    widths = range(len(instance["widths"]))  # the piece widths, numbered from 0 (only how many there are is used)

    model = gp.Model("cutting_stock")

    # patterns_used[p] is how many raw rolls are cut with pattern p.
    patterns_used = model.addVars(patterns, lb=0, vtype=GRB.INTEGER, name="patterns_used")

    # For each width, the pieces of that width cut are at least the number ordered.
    model.addConstrs((gp.quicksum(pieces[p][w] * patterns_used[p] for p in patterns) >= orders[w]
                      for w in widths), name="order")

    # The objective: the total number of raw rolls cut, summed over all patterns, is minimised.
    min_rolls_cut = patterns_used.sum()
    model.setObjective(min_rolls_cut, GRB.MINIMIZE)

    # outputs: how many rolls are cut with each pattern, and the total number of raw rolls cut
    return model, {"patterns_used": [patterns_used[p] for p in patterns],
                   "min_rolls_cut": min_rolls_cut}


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
