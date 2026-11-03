"""Diamond-free degree sequences: a simple graph on N vertices with no diamond and the required degree properties."""
from itertools import combinations

import hexaly.optimizer as hx


def build(instance):
    n = instance["N"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # edge[i][j] = 1 if vertices i and j are adjacent; one decision per unordered pair, no loops
    pair = {(i, j): model.bool() for i, j in combinations(range(n), 2)}
    edge = [[0 if i == j else pair[min(i, j), max(i, j)] for j in range(n)] for i in range(n)]

    # Diamond-free: every set of four vertices spans at most four edges
    for quad in combinations(range(n), 4):
        model.constraint(model.sum(pair[a, b] for a, b in combinations(quad, 2)) <= 4)

    degree = [model.sum(edge[i][j] for j in range(n) if j != i) for i in range(n)]
    # Each degree is positive and a multiple of 3
    for i in range(n):
        model.constraint(degree[i] == 3 * model.int(1, (n - 1) // 3))
    # The degrees add up to a multiple of 12
    model.constraint(model.sum(degree) == 12 * model.int(0, n * (n - 1) // 12))
    # The degree sequence is non-increasing
    for i in range(n - 1):
        model.constraint(degree[i] >= degree[i + 1])

    return optimizer, {"matrix": edge}
