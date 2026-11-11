# csplib_053_graceful_graphs: a PyCSP3 model from DCP Rosetta.
# Download the `csplib_053_graceful_graphs.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_053_graceful_graphs.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python csplib_053_graceful_graphs.py csplib_053_graceful_graphs.json

from pycsp3 import *


def create_model(instance):
    """A labelling of the nodes of a graph with q edges is graceful if each node gets
    a different label from 0, 1, ..., q and, when each edge xy is labelled with the
    difference |f(x) - f(y)| of its end nodes, all the edge labels are different.
    Find a graceful labelling of the graph."""
    graph = instance["graph"]   # graph[e] is the pair of nodes joined by edge e, nodes numbered from 0
    n_nodes = instance["n"]     # number of nodes
    n_edges = instance["m"]     # q, the number of edges, which is also the largest label

    # nodes[x] is the label of node x, a number from 0 to q.
    nodes = VarArray(size=n_nodes, dom=range(n_edges + 1))
    # edges[e] is the label of edge e: the difference of the labels of its two end nodes.
    # The domain starts at 1, since the end labels of an edge differ (a difference of 0 is impossible).
    edges = VarArray(size=n_edges, dom=range(1, n_edges + 1))

    satisfy(
        # Each node has a different label.
        AllDifferent(nodes),
        # Each edge is labelled with the difference of the labels of its two end nodes.
        [edges[e] == abs(nodes[x] - nodes[y]) for e, (x, y) in enumerate(graph)],
        # The edge labels are all different.
        AllDifferent(edges),
    )

    return {"nodes": nodes, "edges": edges}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())
