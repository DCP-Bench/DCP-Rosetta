# coins_grid: a Gurobi (Python) model from DCP Rosetta.
# Download the `coins_grid.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/coins_grid.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python coins_grid.py coins_grid.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Place coins on an n-by-n grid, exactly c in every row and every column, with at most one coin per cell, so that the sum of the squared horizontal distances of the coins from the main diagonal is as small as possible."""
    n = instance["n"]  # the grid is n cells by n cells
    c = instance["c"]  # the number of coins in each row and in each column
    cells = range(n)

    model = gp.Model("coins_grid")

    # x[i, j] is 1 when there is a coin in row i, column j, and 0 when not; a binary variable
    # gives at most one coin per cell
    x = model.addVars(cells, cells, vtype=GRB.BINARY, name="x")

    # Each row holds exactly c coins.
    model.addConstrs((x.sum(i, "*") == c for i in cells), name="row")

    # Each column holds exactly c coins.
    model.addConstrs((x.sum("*", j) == c for j in cells), name="col")

    # z: the sum of the squared horizontal distances of the coins from the main diagonal. A coin in
    # row i, column j is j - i columns from the diagonal, so it costs (i - j)**2.
    z = gp.quicksum((i - j) ** 2 * x[i, j] for i in cells for j in cells)
    model.setObjective(z, GRB.MINIMIZE)

    return model, {"x": [[x[i, j] for j in cells] for i in cells], "z": z}


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
