# csplib_050_diamond_free: a PuLP (Python) model from DCP Rosetta.
# Download the `csplib_050_diamond_free.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_050_diamond_free.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python csplib_050_diamond_free.py csplib_050_diamond_free.json

import itertools

import pulp


def create_model(instance):
    """Find a simple undirected graph on N vertices, given by its adjacency matrix, that has no
    diamond (four vertices joined by five or more edges), no isolated vertex, a degree that is a
    multiple of 3 at every vertex, and a total degree that is a multiple of 12."""
    n = instance["N"]  # the number of vertices

    problem = pulp.LpProblem("diamond_free", pulp.LpMinimize)  # the puzzle asks for a graph only: no objective

    # edge[(i, j)] is 1 when vertices i and j are joined by an edge, and 0 when not. Each pair of vertices is listed once.
    edge = {(i, j): pulp.LpVariable(f"edge_{i}_{j}", cat="Binary")
            for i in range(n) for j in range(i + 1, n)}

    # adjacent(i, j) is 1 when i and j are joined by an edge. An edge has no loops, so a vertex is never joined to itself.
    def adjacent(i, j):
        if i == j:
            return 0
        return edge[(min(i, j), max(i, j))]

    # The adjacency matrix of the graph, one row and one column for each vertex.
    matrix = [[adjacent(i, j) for j in range(n)] for i in range(n)]

    # Each vertex has at least one neighbour, and its degree is a multiple of 3: the degree is 3 * thirds[i],
    # with thirds[i] at least 1.
    for i in range(n):
        thirds = pulp.LpVariable(f"thirds_{i}", 1, (n - 1) // 3, cat="Integer")
        problem += pulp.lpSum(adjacent(i, j) for j in range(n) if j != i) == 3 * thirds

    # The total degree, with each edge counted at both ends, is 12 * twelves: a multiple of 12.
    twelves = pulp.LpVariable("twelves", 0, n * (n - 1) // 12, cat="Integer")
    problem += 2 * pulp.lpSum(edge.values()) == 12 * twelves

    # No diamond: any four vertices have at most four edges among them.
    for a, b, c, d in itertools.combinations(range(n), 4):
        problem += pulp.lpSum([adjacent(a, b), adjacent(a, c), adjacent(a, d),
                               adjacent(b, c), adjacent(b, d), adjacent(c, d)]) <= 4

    return problem, {"matrix": matrix}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
