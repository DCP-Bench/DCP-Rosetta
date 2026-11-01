# csplib_074_maximum_clique: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `csplib_074_maximum_clique.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_074_maximum_clique.html
# Then run it on the first instance (after `pip install ortools`):
#   python csplib_074_maximum_clique.py csplib_074_maximum_clique.json

from ortools.sat.python import cp_model


def create_model(instance):
    """In a simple undirected graph, find a clique (a set of vertices that are all
    pairwise adjacent) of the largest possible size."""
    n_vertices = instance["n"]  # number of vertices
    adj = instance["adj"]       # adj[i][j]: whether vertices i and j are joined by an edge

    model = cp_model.CpModel()

    # c[i] is true when vertex i is in the clique
    c = [model.new_bool_var(f"c_{i}") for i in range(n_vertices)]

    # Two vertices that are not joined by an edge cannot both be in the clique.
    for i in range(n_vertices):
        for j in range(i + 1, n_vertices):
            if adj[i][j] == 0:
                model.add_at_most_one([c[i], c[j]])

    # The clique is as large as possible.
    model.maximize(sum(c))

    return model, {"c": c}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
