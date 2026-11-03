# csplib_050_diamond_free: a Python-MIP (Python) model from DCP Rosetta.
# Download the `csplib_050_diamond_free.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_050_diamond_free.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python csplib_050_diamond_free.py csplib_050_diamond_free.json

import itertools

import mip


def create_model(instance):
    """Find a simple undirected graph on N vertices with no diamond, where a diamond is four
    vertices with at least five edges among them. Every vertex has a degree that is a positive
    multiple of 3, and the degrees sum to a multiple of 12."""
    n = instance["N"]      # the number of vertices
    k_max = (n - 1) // 3   # the largest k for which 3 * k is a possible degree

    model = mip.Model(solver_name="CBC")

    # One variable per pair of vertices: x[i][j] is 1 when vertices i and j are joined by an edge.
    x = [[None] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            x[i][j] = model.add_var(f"x_{i}_{j}", var_type=mip.BINARY)
            x[j][i] = x[i][j]

    # k[i] is one third of the degree of vertex i, from 1 to k_max.
    k = [model.add_var(f"k_{i}", var_type=mip.INTEGER, lb=1, ub=k_max) for i in range(n)]

    # The degree of vertex i, the number of edges at it, is 3 * k[i].
    for i in range(n):
        model += mip.xsum(x[i][j] for j in range(n) if j != i) == 3 * k[i]

    # The degrees are listed from largest to smallest.
    for i in range(n - 1):
        model += k[i] >= k[i + 1]

    # twelfths is the degree sum divided by 12.
    twelfths = model.add_var("twelfths", var_type=mip.INTEGER, lb=0, ub=(n * k_max) // 4)
    # The degrees sum to 12 * twelfths, so their thirds sum to 4 * twelfths.
    model += mip.xsum(k) == 4 * twelfths

    # No diamond: any four vertices are joined by at most four edges.
    for quad in itertools.combinations(range(n), 4):
        model += mip.xsum(x[a][b] for a, b in itertools.combinations(quad, 2)) <= 4

    # The adjacency matrix. A vertex is not joined to itself, so the diagonal is the constant 0.
    matrix = [[mip.LinExpr() if i == j else x[i][j] for j in range(n)] for i in range(n)]
    return model, {"matrix": matrix}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
