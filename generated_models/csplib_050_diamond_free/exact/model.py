# csplib_050_diamond_free: an Exact (Python) model from DCP Rosetta.
# Download the `csplib_050_diamond_free.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_050_diamond_free.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python csplib_050_diamond_free.py csplib_050_diamond_free.json

from itertools import combinations

from exact import Exact


def create_model(instance):
    """Find a simple undirected graph on N vertices that is diamond-free (any four vertices span
    at most four edges), where every vertex has a degree that is a positive multiple of 3 and the
    sum of the degrees is a multiple of 12."""
    n = instance["N"]  # the number of vertices

    solver = Exact()

    # Exact identifies its variables by name.
    # matrix[i][j] is 1 when vertices i and j are joined by an edge, and 0 when not.
    matrix = [[f"matrix_{i}_{j}" for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(n):
            # A vertex is not joined to itself, so its entry on the diagonal is 0.
            upper = 0 if i == j else 1
            solver.addVariable(matrix[i][j], 0, upper)

    # The graph is undirected: an edge from i to j is also an edge from j to i.
    for i in range(n):
        for j in range(i + 1, n):
            solver.addConstraint([(1, matrix[i][j]), (-1, matrix[j][i])], True, 0, True, 0)

    # degree_i_div_3 is the degree of vertex i divided by 3. The degree is positive and at most n - 1.
    thirds = [f"degree_{i}_div_3" for i in range(n)]
    for i in range(n):
        solver.addVariable(thirds[i], 1, (n - 1) // 3)
        # The degree of vertex i, the number of edges at it, is 3 times thirds[i].
        solver.addConstraint([(1, matrix[i][j]) for j in range(n)] + [(-3, thirds[i])], True, 0, True, 0)

    # matrix_total_div_12 is the sum of all degrees divided by 12. The sum is at most n * (n - 1).
    solver.addVariable("matrix_total_div_12", 1, (n * (n - 1)) // 12)
    # The sum of all degrees is a multiple of 12. Each edge counts at both of its ends.
    solver.addConstraint([(1, matrix[i][j]) for i in range(n) for j in range(n)]
                         + [(-12, "matrix_total_div_12")], True, 0, True, 0)

    # Diamond-free: any four vertices span at most four edges.
    for a, b, c, d in combinations(range(n), 4):
        # The six pairs of vertices among a, b, c and d.
        pairs = [(a, b), (a, c), (a, d), (b, c), (b, d), (c, d)]
        solver.addConstraint([(1, matrix[i][j]) for i, j in pairs], False, 0, True, 4)

    return solver, {"matrix": matrix}


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
