# csplib_050_diamond_free: a cvc5 (Python) model from DCP Rosetta.
# Download the `csplib_050_diamond_free.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_050_diamond_free.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python csplib_050_diamond_free.py csplib_050_diamond_free.json

from itertools import combinations

import cvc5.pythonic as c5


def create_model(instance):
    """Find a simple undirected graph on n vertices that is diamond-free (any four
    vertices span at most four edges), where every vertex has a degree that is a
    positive multiple of 3 and the sum of the degrees is a multiple of 12."""
    n = instance["N"]  # the number of vertices

    # edge[(i, j)] with i < j is true when vertices i and j are joined by an edge
    edge = {(i, j): c5.Bool(f"edge_{i}_{j}") for i, j in combinations(range(n), 2)}

    def has_edge(i, j):
        """Whether vertices i and j are joined by an edge."""
        return edge[(min(i, j), max(i, j))]

    solver = c5.Solver()

    # A diamond is four vertices with five or six edges between them, so no five of
    # the six pairs among four vertices may all be joined.
    for quad in combinations(range(n), 4):
        pairs = list(combinations(quad, 2))
        for left_out in pairs:
            solver.add(c5.Or([c5.Not(edge[p]) for p in pairs if p != left_out]))

    # The degree of each vertex is the number of vertices joined to it.
    degree = [c5.Int(f"degree_{i}") for i in range(n)]
    solver.add([
        degree[i] == c5.Sum([c5.If(has_edge(i, j), 1, 0) for j in range(n) if j != i])
        for i in range(n)
    ])

    # Each degree is a positive multiple of 3, and at most n - 1.
    solver.add([c5.Or([d == v for v in range(3, n, 3)]) for d in degree])

    # The degrees are listed in nonincreasing order.
    solver.add([degree[i] >= degree[i + 1] for i in range(n - 1)])

    # The sum of the degrees is twelve times k.
    k = c5.Int("k")
    solver.add(c5.Sum(degree) == 12 * k)

    # The adjacency matrix: entry [i][j] is true when vertices i and j are joined.
    # A vertex is not joined to itself.
    matrix = [[c5.BoolVal(False) if i == j else has_edge(i, j) for j in range(n)] for i in range(n)]

    return solver, {"matrix": matrix}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
