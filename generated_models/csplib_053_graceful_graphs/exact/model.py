# csplib_053_graceful_graphs: an Exact (Python) model from DCP Rosetta.
# Download the `csplib_053_graceful_graphs.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_053_graceful_graphs.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python csplib_053_graceful_graphs.py csplib_053_graceful_graphs.json

from exact import Exact


def create_model(instance):
    """Label the nodes of a graph with m edges with distinct numbers from 0 to m, so
    that the difference between the labels at the two ends of each edge is a different
    number for every edge."""
    n_edges = instance["m"]    # the number of edges, m
    n_nodes = instance["n"]    # the number of nodes
    graph = instance["graph"]  # the two end nodes of each edge

    solver = Exact()

    # Exact identifies its variables by name.
    # nodes[v] is the label of node v, from 0 to m
    nodes = [f"node_{v}" for v in range(n_nodes)]
    # edges[e] is the label of edge e, from 1 to m
    edges = [f"edge_{e}" for e in range(n_edges)]
    # node_has[v][a] is 1 when node v has label a, and 0 when not
    node_has = [{} for _ in range(n_nodes)]
    # edge_has[e][d] is 1 when edge e has label d, and 0 when not
    edge_has = [{} for _ in range(n_edges)]
    for v in range(n_nodes):
        solver.addVariable(nodes[v], 0, n_edges)
        for a in range(n_edges + 1):
            node_has[v][a] = f"node_{v}_has_{a}"
            solver.addVariable(node_has[v][a], 0, 1)
    for e in range(n_edges):
        solver.addVariable(edges[e], 1, n_edges)
        for d in range(1, n_edges + 1):
            edge_has[e][d] = f"edge_{e}_has_{d}"
            solver.addVariable(edge_has[e][d], 0, 1)

    # Each node has exactly one label, and that label is its number.
    for v in range(n_nodes):
        solver.addConstraint([(1, node_has[v][a]) for a in range(n_edges + 1)], True, 1, True, 1)
        solver.addConstraint([(a, node_has[v][a]) for a in range(1, n_edges + 1)] + [(-1, nodes[v])],
                             True, 0, True, 0)

    # Each edge has exactly one label, and that label is its number.
    for e in range(n_edges):
        solver.addConstraint([(1, edge_has[e][d]) for d in range(1, n_edges + 1)], True, 1, True, 1)
        solver.addConstraint([(d, edge_has[e][d]) for d in range(1, n_edges + 1)] + [(-1, edges[e])],
                             True, 0, True, 0)

    # Distinct nodes have distinct labels.
    for a in range(n_edges + 1):
        solver.addConstraint([(1, node_has[v][a]) for v in range(n_nodes)], False, 0, True, 1)

    # Distinct edges have distinct labels.
    for d in range(1, n_edges + 1):
        solver.addConstraint([(1, edge_has[e][d]) for e in range(n_edges)], False, 0, True, 1)

    # An edge joining node u with label a and node v with label b has label |a - b|.
    for e, (u, v) in enumerate(graph):
        for a in range(n_edges + 1):
            for b in range(n_edges + 1):
                if a != b:
                    solver.addConstraint([(1, node_has[u][a]), (1, node_has[v][b]), (-1, edge_has[e][abs(a - b)])],
                                         False, 0, True, 1)

    return solver, {"nodes": nodes, "edges": edges}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
