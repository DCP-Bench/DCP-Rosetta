# csplib_053_graceful_graphs: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `csplib_053_graceful_graphs.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_053_graceful_graphs.html
# Then run it on the first instance (after `pip install ortools`):
#   python csplib_053_graceful_graphs.py csplib_053_graceful_graphs.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Label the nodes of a graph with m edges with distinct numbers from 0..m, so
    that the edge labels |f(x) - f(y)| are all different."""
    m = instance["m"]          # the number of edges
    n = instance["n"]          # the number of nodes
    graph = instance["graph"]  # the two end nodes of each edge

    model = cp_model.CpModel()

    # nodes[v] is the label of node v, taken from 0..m
    nodes = [model.new_int_var(0, m, f"node_{v}") for v in range(n)]
    # edges[e] is the label of edge e, the difference of its end labels, from 1 to m
    edges = [model.new_int_var(1, m, f"edge_{e}") for e in range(m)]

    # Each edge is labelled with the absolute difference of the labels of its two nodes.
    for e, (u, v) in enumerate(graph):
        model.add_abs_equality(edges[e], nodes[u] - nodes[v])
    # All edge labels are different.
    model.add_all_different(edges)
    # All node labels are different.
    model.add_all_different(nodes)

    return model, {"nodes": nodes, "edges": edges}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
