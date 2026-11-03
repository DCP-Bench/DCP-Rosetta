"""Maximal independent set: no two chosen nodes are adjacent, and no further node can be added."""
import hexaly.optimizer as hx


def build(instance):
    n, adjacency = instance["n"], instance["adjacency_list"]  # adjacency[i]: the neighbours of node i, 1-based
    neighbours = [[j - 1 for j in adjacent] for adjacent in adjacency]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # nodes[i] = 1 if node i is in the set
    nodes = [model.bool() for _ in range(n)]

    for i in range(n):
        # Independent: a node in the set has no neighbour in the set
        for j in neighbours[i]:
            model.constraint(nodes[i] + nodes[j] <= 1)
        # Maximal: a node outside the set has a neighbour in it, or it could be added
        model.constraint(nodes[i] + model.sum(nodes[j] for j in neighbours[i]) >= 1)

    return optimizer, {"nodes": nodes}
