# csplib_074_maximum_clique: an Exact (Python) model from DCP Rosetta.
# Download the `csplib_074_maximum_clique.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_074_maximum_clique.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python csplib_074_maximum_clique.py csplib_074_maximum_clique.json

from exact import Exact


def create_model(instance):
    """Find a largest clique in a simple undirected graph: a set of vertices that are all
    pairwise adjacent."""
    n_vertices = instance["n"]  # the vertices are numbered 0 to n_vertices - 1
    adj = instance["adj"]       # adj[i][j] is 1 when vertices i and j are joined by an edge, and 0 otherwise

    solver = Exact()

    # Exact identifies its variables by name.
    # chosen[i] is 1 when vertex i is in the clique, and 0 otherwise
    chosen = [f"c{i}" for i in range(n_vertices)]
    for name in chosen:
        solver.addVariable(name, 0, 1)

    # Two vertices that are not joined by an edge are not both in the clique.
    for i in range(n_vertices):
        for j in range(i + 1, n_vertices):
            if adj[i][j] == 0:
                solver.addConstraint([(1, chosen[i]), (1, chosen[j])], False, 0, True, 1)

    # The clique has as many vertices as possible.
    solver.setObjective([(1, name) for name in chosen], minimize=False)

    return solver, {"c": chosen}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
