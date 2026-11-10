"""Graceful labelling: distinct node labels in 0..m such that the edge labels |f(x) - f(y)| are all different."""
import hexaly.optimizer as hx


def build(instance):
    m, n, graph = instance["m"], instance["n"], instance["graph"]  # graph lists the m edges (0-based nodes)
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # Every node gets a label from 0 to m, no two the same
    nodes = [model.int(0, m) for _ in range(n)]
    for a in range(n):
        for b in range(a + 1, n):
            model.constraint(nodes[a] != nodes[b])

    # An edge is labelled with the difference of its end labels, and the edge labels are all different
    edges = [model.abs(nodes[u] - nodes[v]) for u, v in graph]
    for a in range(len(edges)):
        for b in range(a + 1, len(edges)):
            model.constraint(edges[a] != edges[b])

    return optimizer, {"nodes": nodes, "edges": edges}
