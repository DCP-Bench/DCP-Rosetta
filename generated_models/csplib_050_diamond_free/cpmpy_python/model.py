# csplib_050_diamond_free: a CPMpy model from DCP Rosetta.
# Download the `csplib_050_diamond_free.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_050_diamond_free.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python csplib_050_diamond_free.py csplib_050_diamond_free.json

import itertools

import cpmpy as cp


def create_model(instance):
    """Find a simple undirected graph on n vertices that is diamond-free (any four
    vertices span at most four edges), where every vertex has a degree that is a
    positive multiple of 3 and the sum of the degrees is a multiple of 12."""
    n = instance["N"]  # the number of vertices

    # matrix[i, j] is true when vertices i and j are joined by an edge
    matrix = cp.boolvar(shape=(n, n), name="matrix")

    model = cp.Model()
    # The graph is undirected: an edge from i to j is also an edge from j to i.
    model.add(matrix == matrix.T)
    # The graph is simple: no vertex has an edge to itself.
    for i in range(n):
        model.add(~matrix[i, i])
    # Each vertex has a degree above zero that is a multiple of 3.
    for i in range(n):
        model.add(cp.sum(matrix[i]) > 0)
        model.add(cp.sum(matrix[i]) % 3 == 0)
    # The sum of the degrees (each edge counted twice) is a multiple of 12.
    model.add(cp.sum(matrix) % 12 == 0)
    # Diamond-free: any four vertices span at most four of their six possible edges.
    for a, b, c, d in itertools.combinations(range(n), 4):
        model.add((matrix[a, b] + matrix[a, c] + matrix[a, d]
                  + matrix[b, c] + matrix[b, d] + matrix[c, d]) <= 4)

    return model, {"matrix": matrix}


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
