# csplib_074_maximum_clique: a SCIP (Python) model from DCP Rosetta.
# Download the `csplib_074_maximum_clique.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_074_maximum_clique.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python csplib_074_maximum_clique.py csplib_074_maximum_clique.json

from pyscipopt import Model


def create_model(instance):
    """Given an undirected graph G = (V, E), find a clique of the largest possible size:
    a set of vertices in which every two distinct vertices are joined by an edge."""
    n = instance["n"]       # the number of vertices, numbered 0 .. n-1
    adj = instance["adj"]   # adj[i][j] is 1 when vertices i and j are joined by an edge, 0 when not

    model = Model("maximum_clique")

    # c[i] is 1 when vertex i is in the clique, and 0 when not
    c = model.addMatrixVar(n, vtype="B", name="c")

    # Two distinct vertices with no edge between them cannot both be in the clique.
    # The graph is undirected, so each pair is checked once, with i < j.
    for i in range(n):
        for j in range(i + 1, n):
            if not adj[i][j]:
                model.addCons(c[i] + c[j] <= 1)

    # The clique size is the number of chosen vertices; maximise it.
    model.setObjective(c.sum(), "maximize")

    return model, {"c": c}


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
