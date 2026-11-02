# csplib_053_graceful_graphs: a cvc5 (Python) model from DCP Rosetta.
# Download the `csplib_053_graceful_graphs.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_053_graceful_graphs.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python csplib_053_graceful_graphs.py csplib_053_graceful_graphs.json

import cvc5.pythonic as c5


def create_model(instance):
    """Label the nodes of a graph with m edges with distinct numbers from 0 to m, so
    that the edge labels |f(x) - f(y)| are all different."""
    n = instance["n"]          # the number of nodes
    m = instance["m"]          # the number of edges
    graph = instance["graph"]  # graph[k] = [x, y]: the two end nodes of edge k

    # nodes[v] is the label of node v
    nodes = [c5.Int(f"node_{v}") for v in range(n)]
    # edges[k] is the label of edge k
    edges = [c5.Int(f"edge_{k}") for k in range(m)]

    solver = c5.Solver()

    # Node labels are from 0 to m.
    for v in nodes:
        solver.add(v >= 0, v <= m)

    # Node labels are different.
    if n >= 2:
        solver.add(c5.Distinct(nodes))

    # An edge is labelled with the difference of its end labels. The end labels are
    # different, so the edge label is from 1 to m.
    for k, (x, y) in enumerate(graph):
        fx, fy = nodes[x], nodes[y]
        solver.add(
            c5.Or(
                c5.And(fx >= fy, edges[k] == fx - fy),
                c5.And(fy > fx, edges[k] == fy - fx),
            )
        )
        solver.add(edges[k] >= 1, edges[k] <= m)

    # Edge labels are different. There are m of them, from 1 to m, so they add up to
    # 1 + 2 + ... + m.
    if m >= 2:
        solver.add(c5.Distinct(edges))
        solver.add(c5.Sum(edges) == m * (m + 1) // 2)

    return solver, {"nodes": nodes, "edges": edges}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
