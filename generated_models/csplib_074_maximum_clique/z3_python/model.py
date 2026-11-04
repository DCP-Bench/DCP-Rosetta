# csplib_074_maximum_clique: a Z3 (Python) model from DCP Rosetta.
# Download the `csplib_074_maximum_clique.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_074_maximum_clique.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python csplib_074_maximum_clique.py csplib_074_maximum_clique.json

import z3


def create_model(instance):
    """In a simple undirected graph, find a clique (a set of vertices that are all
    pairwise adjacent) of the largest possible size."""
    n = instance["n"]      # number of vertices
    adj = instance["adj"]  # adj[i][j] is 1 when vertices i and j are joined by an edge, else 0

    # c[i] is true when vertex i is in the clique
    c = [z3.Bool(f"c_{i}") for i in range(n)]

    solver = z3.Optimize()

    # Two vertices that are not joined by an edge cannot both be in the clique.
    solver.add([z3.Not(z3.And(c[i], c[j]))
                for i in range(n) for j in range(i + 1, n) if adj[i][j] == 0])

    # number of vertices in the clique
    size = z3.Sum([z3.If(ci, 1, 0) for ci in c])
    solver.maximize(size)

    return solver, {"c": c}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
