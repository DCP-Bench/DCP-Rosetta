# csplib_053_graceful_graphs: a CPMpy model from DCP Rosetta.
# Download the `csplib_053_graceful_graphs.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_053_graceful_graphs.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python csplib_053_graceful_graphs.py csplib_053_graceful_graphs.json

import numpy as np
import cpmpy as cp


def create_model(instance):
    """Label the nodes of a graph with m edges with distinct numbers from 0..m, so
    that the edge labels |f(x) - f(y)| are all different."""
    m = instance["m"]                    # the number of edges
    n = instance["n"]                    # the number of nodes
    graph = np.array(instance["graph"])  # graph[k] = [x, y]: the two end nodes of edge k

    # nodes[x] is the label of node x; labels come from 0..m
    nodes = cp.intvar(0, m, shape=n, name="nodes")
    # edges[k] is the label of edge k: the difference of its end labels, so at least 1
    # (node labels are distinct) and at most m
    edges = cp.intvar(1, m, shape=m, name="edges")

    model = cp.Model()
    # Each edge is labelled with the absolute difference of the labels of its two nodes.
    model.add(cp.abs(nodes[graph[:, 0]] - nodes[graph[:, 1]]) == edges)
    # All edge labels are different.
    model.add(cp.AllDifferent(edges))
    # All node labels are different.
    model.add(cp.AllDifferent(nodes))

    return model, {"nodes": nodes, "edges": edges}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
