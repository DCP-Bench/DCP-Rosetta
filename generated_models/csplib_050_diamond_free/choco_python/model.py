# csplib_050_diamond_free: a Choco-solver (Python) model from DCP Rosetta.
# Download the `csplib_050_diamond_free.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_050_diamond_free.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python csplib_050_diamond_free.py csplib_050_diamond_free.json

from itertools import combinations

from pychoco.model import Model


def create_model(instance):
    """Find the adjacency matrix of a simple undirected graph on N vertices with no isolated
    vertex, where every degree is a multiple of 3, the degrees sum to a multiple of 12, and no
    four vertices are joined by five or more edges (no diamond)."""
    n = instance["N"]  # the number of vertices

    model = Model()

    # edge[a, b] is true when vertices a < b are joined by an edge
    edge = {}
    for a, b in combinations(range(n), 2):
        edge[a, b] = model.boolvar(name=f"edge_{a}_{b}")

    # A vertex is never joined to itself, so the diagonal is false.
    no_loop = model.boolvar(value=False)

    # matrix[a][b] is true when vertices a and b are joined; joining is symmetric.
    matrix = [[edge[min(a, b), max(a, b)] if a != b else no_loop for b in range(n)]
              for a in range(n)]

    # degrees[a] is the number of edges at vertex a, a positive multiple of 3.
    degrees = []
    for a in range(n):
        degree = model.intvar(list(range(3, n, 3)), name=f"degree_{a}")
        model.sum(matrix[a], "=", degree).post()
        degrees.append(degree)

    # The degrees sum to a multiple of 12. Each edge is counted at both of its ends.
    degree_sum = model.intvar(list(range(12, n * (n - 1) + 1, 12)), name="degree_sum")
    model.sum(degrees, "=", degree_sum).post()

    # No four vertices are joined by five or more edges.
    for a, b, c, d in combinations(range(n), 4):
        model.sum([matrix[a][b], matrix[a][c], matrix[a][d],
                   matrix[b][c], matrix[b][d], matrix[c][d]], "<=", 4).post()

    return model, {"matrix": matrix}, None


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
