# csplib_074_maximum_clique: a Python-MIP (Python) model from DCP Rosetta.
# Download the `csplib_074_maximum_clique.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_074_maximum_clique.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python csplib_074_maximum_clique.py csplib_074_maximum_clique.json

import mip


def create_model(instance):
    """In a simple undirected graph, find a clique (a set of vertices that are all
    pairwise adjacent) of the largest possible size."""
    n = instance["n"]      # number of vertices
    adj = instance["adj"]  # adj[i][j] is 1 when vertices i and j are joined by an edge, and 0 when not

    model = mip.Model(sense=mip.MAXIMIZE, solver_name="CBC")

    # c[i] is 1 when vertex i is in the clique, and 0 when not
    c = [model.add_var(f"c_{i}", var_type=mip.BINARY) for i in range(n)]

    # Two vertices that are not joined by an edge cannot both be in the clique.
    for i in range(n):
        for j in range(i + 1, n):
            if adj[i][j] == 0 or adj[j][i] == 0:
                model.add_constr(c[i] + c[j] <= 1)

    # The clique is as large as possible.
    model.objective = mip.xsum(c)

    return model, {"c": c}


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
