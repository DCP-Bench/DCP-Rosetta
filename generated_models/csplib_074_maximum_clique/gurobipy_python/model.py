# csplib_074_maximum_clique: a Gurobi (Python) model from DCP Rosetta.
# Download the `csplib_074_maximum_clique.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_074_maximum_clique.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python csplib_074_maximum_clique.py csplib_074_maximum_clique.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Maximum clique: choose as many vertices as possible so that every two chosen vertices are joined by an edge."""
    n = instance["n"]      # the number of vertices, numbered from 0
    adj = instance["adj"]  # adj[i][j]: 1 when vertices i and j are joined by an edge, 0 when not (only i < j is read)
    vertices = range(n)
    # Each pair i < j once: the graph is undirected.
    pairs = [(i, j) for i in vertices for j in vertices if i < j]

    model = gp.Model("maximum_clique")

    # c[i] is 1 when vertex i is in the clique, and 0 when not.
    c = model.addVars(vertices, vtype=GRB.BINARY, name="c")

    # Two vertices that are not joined by an edge cannot both be in the clique.
    model.addConstrs((c[i] + c[j] <= 1 for i, j in pairs if adj[i][j] == 0), name="non_edge")

    # The clique's size is the number of vertices chosen; make it as large as possible.
    model.setObjective(c.sum(), GRB.MAXIMIZE)

    return model, {"c": [c[i] for i in vertices]}


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
