# csplib_050_diamond_free: a hermax (Python) model from DCP Rosetta.
# Download the `csplib_050_diamond_free.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_050_diamond_free.html
# Then run it on the first instance (after `pip install hermax`):
#   python csplib_050_diamond_free.py csplib_050_diamond_free.json

from itertools import combinations

from hermax.model import Model


def create_model(instance):
    """Find a simple undirected graph on N vertices, given as its adjacency matrix, such that
    every vertex has a positive degree that is a multiple of 3, the degrees are listed in
    non-increasing order, the sum of all degrees is a multiple of 12, and the graph is
    diamond-free (no four vertices are joined by five or more edges)."""
    n = instance["N"]  # N: the number of vertices of the graph

    m = Model()

    # adjacent[i][j] is true when vertices i and j are joined by an edge
    adjacent = m.bool_matrix("adjacent", n, n)

    # The graph is simple and undirected: no vertex is adjacent to itself,
    # and adjacency is symmetric.
    for i in range(n):
        m &= ~adjacent[i][i]
    for i in range(n):
        for j in range(i + 1, n):
            m &= (~adjacent[i][j] | adjacent[j][i])
            m &= (adjacent[i][j] | ~adjacent[j][i])

    # The degree of vertex i is its number of neighbours. It is a positive multiple
    # of 3 and at most n - 1, so it is 3 * k[i] with k[i] in 1..(n-1)//3.
    max_k = (n - 1) // 3
    # k[i] is one third of the degree of vertex i
    k = m.int_vector("k", n, 1, max_k)
    for i in range(n):
        # the number of neighbours of vertex i is three times k[i]
        m &= (sum(adjacent[i][j] for j in range(n)) == 3 * k[i])

    # The degree sequence is non-increasing: d_1 >= d_2 >= ... >= d_n, which is
    # k[i] >= k[i + 1] since each degree is three times k.
    for i in range(n - 1):
        m &= (k[i] >= k[i + 1])

    # The sum of all degrees is a multiple of 12. The degrees add up to 3 * sum(k),
    # so sum(k) must equal 4 * t for some whole number t (t is the number of fours).
    t = m.int("t", 0, n * max_k // 4)
    m &= (sum(k[i] for i in range(n)) == 4 * t)

    # Diamond-free: a diamond is four vertices joined by at least five edges, so
    # among any four vertices at most four of the six possible edges are present.
    for quad in combinations(range(n), 4):
        m &= (sum(adjacent[a][b] for a, b in combinations(quad, 2)) <= 4)

    # The adjacency matrix is the answer; the problem has no objective.
    return m, {"matrix": adjacent}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
