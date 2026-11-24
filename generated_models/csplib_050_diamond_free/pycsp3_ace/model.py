# csplib_050_diamond_free: a PyCSP3 model from DCP Rosetta.
# Download the `csplib_050_diamond_free.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_050_diamond_free.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python csplib_050_diamond_free.py csplib_050_diamond_free.json

from pycsp3 import *


def create_model(instance):
    """Find a simple undirected graph on N vertices with no diamond as an induced
    subgraph (among any four vertices at most four pairs are adjacent), in which
    every vertex has a degree that is positive and divisible by 3, and the sum of
    the degrees is divisible by 12."""
    n_vertices = instance["N"]  # N, the number of vertices
    degree_step = 3             # every degree is a positive multiple of this
    degree_sum_step = 12        # the sum of the degrees is a multiple of this
    max_edges = 4               # at most this many of the six pairs of four vertices are adjacent

    # matrix[u][v] is 1 when vertices u and v are adjacent, 0 otherwise.
    matrix = VarArray(size=[n_vertices, n_vertices], dom={0, 1})
    # degree[v] is the degree of vertex v: a positive multiple of degree_step, at most N - 1.
    degree = VarArray(size=n_vertices, dom=range(degree_step, n_vertices, degree_step))

    satisfy(
        # The graph is simple: there are no loop edges, so no vertex is adjacent to itself.
        [matrix[v][v] == 0 for v in range(n_vertices)],
        # The graph is undirected: u is adjacent to v exactly when v is adjacent to u.
        [matrix[u][v] == matrix[v][u] for u in range(n_vertices) for v in range(u + 1, n_vertices)],
        # The degree of each vertex is the number of its adjacent vertices.
        [degree[v] == Sum(matrix[v]) for v in range(n_vertices)],
        # The sum of the degrees is divisible by 12, i.e. the number of edges is divisible by 6.
        Sum(degree) % degree_sum_step == 0,
        # The graph is diamond-free: among any four vertices at most four pairs are adjacent.
        [
            matrix[a][b] + matrix[a][c] + matrix[a][d] + matrix[b][c] + matrix[b][d] + matrix[c][d] <= max_edges
            for a in range(n_vertices)
            for b in range(a + 1, n_vertices)
            for c in range(b + 1, n_vertices)
            for d in range(c + 1, n_vertices)
        ],
    )

    return {"matrix": matrix}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        print("matrix", "=")
        for row in outputs["matrix"]:
            print(values(row))
    else:
        print("No solution:", status())
