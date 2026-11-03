# csplib_053_graceful_graphs: a hermax (Python) model from DCP Rosetta.
# Download the `csplib_053_graceful_graphs.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_053_graceful_graphs.html
# Then run it on the first instance (after `pip install hermax`):
#   python csplib_053_graceful_graphs.py csplib_053_graceful_graphs.json

from hermax.model import Model


def create_model(instance):
    """Graceful graphs: give every node a different label from 0..q, where q is the number
    of edges, so that labelling each edge xy with |f(x) - f(y)| gives every edge a
    different label. Any such labelling is a solution; there is no objective."""
    edge_count = instance["m"]   # q: the number of edges of the graph
    node_count = instance["n"]   # the number of nodes, numbered 0..n-1
    graph = instance["graph"]    # graph[e] = [u, v]: the two end nodes of edge e

    m = Model()

    # nodes[v] is the label of node v, one of 0..q
    nodes = m.int_vector("nodes", node_count, 0, edge_count)
    # edges[e] is the label of edge e: the absolute difference of its end labels, 1..q
    edges = m.int_vector("edges", edge_count, 1, edge_count)

    # The node labels are all different.
    m &= nodes.all_different()
    # The edge labels are all different.
    m &= edges.all_different()

    # forward[e] is true when the first end of edge e has the larger label, which fixes
    # the sign of the difference, so that the edge label is the absolute difference.
    forward = m.bool_vector("forward", edge_count)
    for e, (u, v) in enumerate(graph):
        # The label of edge e is the difference of its end labels, larger minus smaller.
        m &= (edges[e] == nodes[u] - nodes[v]).only_if(forward[e])
        m &= (edges[e] == nodes[v] - nodes[u]).only_if(~forward[e])

    return m, {"nodes": nodes, "edges": edges}


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
