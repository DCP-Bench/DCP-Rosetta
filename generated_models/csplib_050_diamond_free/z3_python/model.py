# csplib_050_diamond_free: a Z3 (Python) model from DCP Rosetta.
# Download the `csplib_050_diamond_free.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_050_diamond_free.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python csplib_050_diamond_free.py csplib_050_diamond_free.json

import itertools

import z3


def create_model(instance):
    """Find a simple undirected graph on N vertices with no diamond, where every vertex has
    a degree that is a positive multiple of 3 and the degrees sum to a multiple of 12."""
    n_vertices = instance["N"]  # the number of vertices

    # matrix[i][j] is true when vertices i and j are joined by an edge
    matrix = [[z3.Bool(f"matrix_{i}_{j}") for j in range(n_vertices)] for i in range(n_vertices)]

    # The number of edges among the given cells of the matrix.
    def count(cells):
        return z3.Sum([z3.If(cell, 1, 0) for cell in cells])

    solver = z3.Solver()

    # The graph constraints, collected per vertex below.
    for i in range(n_vertices):
        # Each vertex has a degree above zero that is a multiple of 3.
        solver.add(count(matrix[i]) > 0)
        solver.add(count(matrix[i]) % 3 == 0)

        # No vertex is joined to itself.
        solver.add(z3.Not(matrix[i][i]))

        # The graph is undirected: an edge from i to j is also an edge from j to i.
        for j in range(i + 1, n_vertices):
            solver.add(matrix[i][j] == matrix[j][i])

    # The degrees sum to a multiple of 12, so the number of edges is a multiple of 6.
    solver.add(count([cell for row in matrix for cell in row]) % 12 == 0)

    # Diamond-free: any four vertices have at most four edges among them.
    for a, b, c, d in itertools.combinations(range(n_vertices), 4):
        # The six pairs of the four vertices a, b, c and d.
        pairs = [matrix[a][b], matrix[a][c], matrix[a][d],
                 matrix[b][c], matrix[b][d], matrix[c][d]]
        solver.add(count(pairs) <= 4)

    return solver, {"matrix": matrix}


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
