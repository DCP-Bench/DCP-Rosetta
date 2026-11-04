# csplib_053_graceful_graphs: a Python-MIP (Python) model from DCP Rosetta.
# Download the `csplib_053_graceful_graphs.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_053_graceful_graphs.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python csplib_053_graceful_graphs.py csplib_053_graceful_graphs.json

import mip


def create_model(instance):
    """Label the nodes of a graph with m edges with distinct numbers from 0..m, so
    that the edge labels |f(x) - f(y)| are all different."""
    n_nodes = instance["n"]          # the number of nodes
    n_edges = instance["m"]          # the number of edges
    graph = instance["graph"]        # graph[k] = [x, y]: the two end nodes of edge k
    labels = range(n_edges + 1)      # the node labels 0..n_edges
    pairs = [(a, b) for a in labels for b in labels if a != b]  # ordered pairs of different labels

    model = mip.Model(solver_name="CBC")

    # p[i][a] is 1 when node i has label a, and 0 when not
    p = [[model.add_var(f"p_{i}_{a}", var_type=mip.BINARY) for a in labels]
         for i in range(n_nodes)]
    # f[i] is the label of node i
    f = [model.add_var(f"f_{i}", lb=0, ub=n_edges, var_type=mip.INTEGER)
         for i in range(n_nodes)]

    # Each node has exactly one label, and f[i] is that label.
    for i in range(n_nodes):
        model += mip.xsum(p[i]) == 1
        model += f[i] == mip.xsum(a * p[i][a] for a in labels)

    # Each label is given to at most one node.
    for a in labels:
        model += mip.xsum(p[i][a] for i in range(n_nodes)) <= 1

    # z[k][a, b] is 1 when edge k joins a node labelled a to a node labelled b, and 0 when not
    z = [{(a, b): model.add_var(f"z_{k}_{a}_{b}", lb=0, ub=1) for (a, b) in pairs}
         for k in range(n_edges)]
    # e[k] is the label of edge k
    e = [model.add_var(f"e_{k}", lb=1, ub=n_edges, var_type=mip.INTEGER)
         for k in range(n_edges)]

    # The two ends of edge k carry the labels of its nodes x and y.
    for k, (x, y) in enumerate(graph):
        for a in labels:
            model += mip.xsum(z[k][a, b] for b in labels if b != a) == p[x][a]
        for b in labels:
            model += mip.xsum(z[k][a, b] for a in labels if a != b) == p[y][b]

    # The label of edge k is the gap between the end labels of edge k.
    for k in range(n_edges):
        model += e[k] == mip.xsum(abs(a - b) * z[k][a, b] for (a, b) in pairs)

    # Each gap d from 1 to n_edges is the label of exactly one edge.
    for d in range(1, n_edges + 1):
        model += mip.xsum(z[k][a, b] for k in range(n_edges) for (a, b) in pairs
                          if abs(a - b) == d) == 1

    return model, {"nodes": f, "edges": e}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
