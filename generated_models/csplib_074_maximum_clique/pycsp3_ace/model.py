# csplib_074_maximum_clique: a PyCSP3 model from DCP Rosetta.
# Download the `csplib_074_maximum_clique.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_074_maximum_clique.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python csplib_074_maximum_clique.py csplib_074_maximum_clique.json

from pycsp3 import *


def create_model(instance):
    """Given a simple undirected graph G = (V, E), a clique is a subset of vertices in which every two
    distinct vertices are adjacent. Find a clique of the largest possible size."""
    # n: the number of vertices, numbered 0 to n - 1.
    n = instance["n"]

    # adj[i][j] is 1 when vertices i and j are joined by an edge, 0 otherwise. The graph is undirected,
    # so only the pairs with i < j are read.
    adj = instance["adj"]

    # c[i] is 1 when vertex i is in the clique, 0 otherwise.
    c = VarArray(size=n, dom={0, 1})

    satisfy(
        # Two distinct vertices that are not adjacent cannot both be in the clique.
        [c[i] + c[j] <= 1 for i in range(n) for j in range(i + 1, n) if adj[i][j] == 0]
    )

    # The clique size is the number of chosen vertices, to be maximised.
    maximize(Sum(c))

    return {"c": c}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is OPTIMUM:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())
