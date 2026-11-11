# csplib_050_diamond_free: a Gurobi (Python) model from DCP Rosetta.
# Download the `csplib_050_diamond_free.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_050_diamond_free.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python csplib_050_diamond_free.py csplib_050_diamond_free.json

import gurobipy as gp
from gurobipy import GRB
from itertools import combinations


def create_model(instance):
    """Find a simple undirected graph on N vertices, with no isolated vertex, every vertex degree
    a multiple of 3, the sum of all degrees a multiple of 12, and no diamond: no four vertices
    joined by five or six edges among them."""
    n = instance["N"]  # the number of vertices, numbered 0 to N-1
    vertices = range(n)

    model = gp.Model("diamond_free")

    # edge[i, j] (i < j) is 1 when vertices i and j are joined by an edge. The graph is undirected
    # and has no loops, so this one variable gives both matrix entries (i, j) and (j, i).
    edge = model.addVars(list(combinations(vertices, 2)), vtype=GRB.BINARY, name="edge")

    def joined(i, j):
        # 1 when i and j are joined, whichever order they are given in
        return edge[min(i, j), max(i, j)]

    # degree[i] is the number of edges at vertex i.
    degree = [gp.quicksum(joined(i, j) for j in vertices if j != i) for i in vertices]

    # Every vertex has degree greater than zero: no isolated vertices.
    model.addConstrs((degree[i] >= 1 for i in vertices), name="has_edge")

    # thirds[i] is degree[i] / 3, so every degree is a multiple of 3 (the rule is 3 in the problem).
    # A vertex has at most n - 1 neighbours, which bounds thirds[i].
    thirds = model.addVars(vertices, lb=0, ub=(n - 1) // 3, vtype=GRB.INTEGER, name="thirds")
    model.addConstrs((degree[i] == 3 * thirds[i] for i in vertices), name="degree_mod3")

    # twelfths is the sum of all degrees divided by 12 (the rule is 12 in the problem). The degree
    # sum is twice the number of edges, so the number of edges is a multiple of 6.
    twelfths = model.addVar(lb=0, ub=n * (n - 1) // 12, vtype=GRB.INTEGER, name="twelfths")
    model.addConstr(gp.quicksum(degree) == 12 * twelfths, name="degree_sum_mod12")

    # No diamond: among any four vertices at most four of the six possible edges are present
    # (five or more edges would be a diamond).
    model.addConstrs((joined(a, b) + joined(a, c) + joined(a, d) + joined(b, c) + joined(b, d)
                      + joined(c, d) <= 4 for a, b, c, d in combinations(vertices, 4)),
                     name="no_diamond")

    # matrix[i][j] is 1 when vertices i and j are joined; the diagonal is 0 (no loops).
    matrix = [[0 if i == j else joined(i, j) for j in vertices] for i in vertices]
    return model, {"matrix": matrix}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.Params.OutputFlag = 0  # no solver log
    model.optimize()

    if model.Status == GRB.OPTIMAL:  # a solution
        # a variable's value is var.X, an expression's is expr.getValue(); both read through LinExpr
        value = np.vectorize(lambda out: round(gp.LinExpr(out).getValue()))
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution, Gurobi status", model.Status)  # 3 infeasible, 4 infeasible or unbounded
