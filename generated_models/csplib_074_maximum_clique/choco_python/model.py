# csplib_074_maximum_clique: a Choco-solver (Python) model from DCP Rosetta.
# Download the `csplib_074_maximum_clique.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_074_maximum_clique.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python csplib_074_maximum_clique.py csplib_074_maximum_clique.json

from pychoco.model import Model


def create_model(instance):
    """In a simple undirected graph, find a clique (a set of vertices that are all
    pairwise adjacent) of the largest possible size."""
    n = instance["n"]      # number of vertices
    adj = instance["adj"]  # adj[i][j] is 1 when vertices i and j are joined by an edge, else 0

    model = Model()

    # c[i] is 1 when vertex i is in the clique
    c = [model.boolvar(name=f"c_{i}") for i in range(n)]

    # Two vertices that are not joined by an edge cannot both be in the clique.
    for i in range(n):
        for j in range(i + 1, n):
            if adj[i][j] == 0:
                model.sum([c[i], c[j]], "<=", 1).post()

    # The size of the clique, to be made as large as possible.
    size = model.intvar(0, n, name="size")
    model.sum(c, "=", size).post()

    return model, {"c": c}, {"objective": size, "maximize": True}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
