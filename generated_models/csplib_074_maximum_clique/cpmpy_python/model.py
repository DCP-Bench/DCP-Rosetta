# csplib_074_maximum_clique: a CPMpy model from DCP Rosetta.
# Download the `csplib_074_maximum_clique.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_074_maximum_clique.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python csplib_074_maximum_clique.py csplib_074_maximum_clique.json

import cpmpy as cp


def create_model(instance):
    """In a simple undirected graph, find a clique (a set of vertices that are all
    pairwise adjacent) of the largest possible size."""
    n = instance["n"]      # number of vertices
    adj = instance["adj"]  # adj[i][j] is 1 when vertices i and j are joined by an edge, else 0

    # c[i] is true when vertex i is in the clique
    c = cp.boolvar(shape=n, name="c")

    model = cp.Model()

    # Two vertices that are not adjacent cannot both be in the clique.
    for i in range(n):
        for j in range(i + 1, n):
            if adj[i][j] == 0:
                model.add(c[i] + c[j] <= 1)

    # The clique is as large as possible.
    model.maximize(cp.sum(c))

    return model, {"c": c}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
