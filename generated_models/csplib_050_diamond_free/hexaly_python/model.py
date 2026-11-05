"""Diamond-free degree sequences: a simple graph on N vertices with no diamond and the required degree properties."""
from itertools import combinations

import hexaly.optimizer as hx


def build(instance):
    n = instance["N"]  # N = number of vertices of the graph
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # pair[i, j] = 1 if the edge {i, j} is in the graph; one Boolean per unordered pair i < j
    pair = {(i, j): model.bool() for i, j in combinations(range(n), 2)}
    # edge[i][j] = the adjacency matrix: 1 if vertices i and j are adjacent. It is symmetric, and 0 on the
    # diagonal because the graph is simple (no loop edges).
    edge = [[0 if i == j else pair[min(i, j), max(i, j)] for j in range(n)] for i in range(n)]

    # Diamond-free: a diamond is four vertices with at least five edges between them, so every set of
    # four vertices spans at most four edges
    for quad in combinations(range(n), 4):
        model.constraint(model.sum(pair[a, b] for a, b in combinations(quad, 2)) <= 4)

    # degree[i] = the number of edges incident on vertex i
    degree = [model.sum(edge[i][j] for j in range(n) if j != i) for i in range(n)]
    # Each degree is positive (no isolated vertex) and a multiple of 3. The unnamed integer is degree / 3:
    # at least 1, and at most (n - 1) // 3 because a degree is at most n - 1.
    for i in range(n):
        model.constraint(degree[i] == 3 * model.int(1, (n - 1) // 3))
    # The degrees add up to a multiple of 12 (so the number of edges is a multiple of 6). The unnamed
    # integer is that sum / 12, at most n * (n - 1) // 12 because the sum is at most n * (n - 1).
    model.constraint(model.sum(degree) == 12 * model.int(0, n * (n - 1) // 12))
    # The degree sequence is non-increasing: d_i >= d_{i+1}
    for i in range(n - 1):
        model.constraint(degree[i] >= degree[i + 1])

    return optimizer, {"matrix": edge}
