# csplib_053_graceful_graphs: a Z3 (Python) model from DCP Rosetta.
# Download the `csplib_053_graceful_graphs.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_053_graceful_graphs.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python csplib_053_graceful_graphs.py csplib_053_graceful_graphs.json

import z3


def create_model(instance):
    """Label the nodes of a graph with m edges with distinct numbers from 0..m, so
    that the edge labels |f(x) - f(y)| are all different."""
    m = instance["m"]          # the number of edges
    n = instance["n"]          # the number of nodes
    graph = instance["graph"]  # graph[e] = [u, v]: the two end nodes of edge e

    # nodes[v] is the label of node v
    nodes = [z3.Int(f"node_{v}") for v in range(n)]
    # edges[e] is the label of edge e
    edges = [z3.Int(f"edge_{e}") for e in range(m)]

    solver = z3.Solver()
    # Node labels are numbers from 0 to m.
    for label in nodes:
        solver.add(label >= 0, label <= m)
    # Edge labels are numbers from 1 to m, since the end labels of an edge differ.
    for label in edges:
        solver.add(label >= 1, label <= m)

    # Each edge is labelled with the difference of the labels of its two end nodes.
    for e, (u, v) in enumerate(graph):
        solver.add(edges[e] == z3.Abs(nodes[u] - nodes[v]))

    # All edge labels are different.
    solver.add(z3.Distinct(edges))
    # All node labels are different.
    solver.add(z3.Distinct(nodes))

    return solver, {"nodes": nodes, "edges": edges}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
