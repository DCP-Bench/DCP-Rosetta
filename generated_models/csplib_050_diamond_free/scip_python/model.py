# csplib_050_diamond_free: a SCIP (Python) model from DCP Rosetta.
# Download the `csplib_050_diamond_free.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_050_diamond_free.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python csplib_050_diamond_free.py csplib_050_diamond_free.json

from itertools import combinations

from pyscipopt import Model, quicksum


def create_model(instance):
    """Find a simple undirected graph on N vertices (no loops, no multiple edges)
    that is diamond-free, that has every vertex of positive degree divisible by 3,
    whose degrees are listed in non-increasing order, and whose degree sum is a
    multiple of 12. A diamond is four vertices spanning at least five edges.
    The output "matrix" is the adjacency matrix of such a graph."""
    n = instance["N"]  # the number of vertices of the graph

    model = Model("csplib_050_diamond_free")

    # x[i, j] is 1 when vertices i and j are joined by an edge, and 0 when not.
    # A simple graph has no loops, so the diagonal is fixed to 0 by its upper bound.
    no_loop = [[0 if i == j else 1 for j in range(n)] for i in range(n)]
    x = model.addMatrixVar((n, n), vtype="B", name="x", ub=no_loop)

    # The graph is undirected: the edge {i, j} is the edge {j, i}, so the matrix is symmetric.
    model.addMatrixCons(x == x.T)

    # k[i] is the degree of vertex i divided by 3, so the degree is 3 * k[i].
    # The degree is positive and divisible by 3 (our reading of "modulo 3"), so k[i] >= 1.
    # A vertex has at most n - 1 neighbours (no loops, no multiple edges), so k[i] <= (n - 1) // 3.
    k = model.addMatrixVar(n, vtype="I", name="k", lb=1, ub=(n - 1) // 3)

    # The degree of each vertex is 3 * k[i], the row sum of the adjacency matrix.
    model.addMatrixCons(x.sum(axis=1) == 3 * k)

    # The degree sequence is listed in non-increasing order: d[i] >= d[i + 1].
    # Dividing by 3 keeps this order, so it is written on k.
    model.addMatrixCons(k[:-1] >= k[1:])

    # The sum of the degrees, the sum of all entries of x, is a multiple of 12.
    # m is the quotient. Its bound n * (n - 1) / 12 comes from the degrees being at most n - 1.
    m = model.addVar(vtype="I", lb=0, ub=n * (n - 1) // 12, name="m")
    model.addCons(x.sum() == 12 * m)

    # Diamond-free: among any four vertices at most 4 of the 6 possible edges are present.
    # The edges among four vertices are the edges of their induced subgraph, so this is the
    # statement's condition. One constraint is posted for each four-vertex set.
    for quad in combinations(range(n), 4):
        model.addCons(quicksum(x[p, q] for p, q in combinations(quad, 2)) <= 4)

    # The problem is a satisfaction problem: any graph meeting the constraints is an answer,
    # so no objective is set.
    return model, {"matrix": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
