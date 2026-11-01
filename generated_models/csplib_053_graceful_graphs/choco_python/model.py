# csplib_053_graceful_graphs: a Choco-solver (Python) model from DCP Rosetta.
# Download the `csplib_053_graceful_graphs.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_053_graceful_graphs.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python csplib_053_graceful_graphs.py csplib_053_graceful_graphs.json

from pychoco.model import Model


def create_model(instance):
    """Label the nodes of a graph with distinct numbers from 0 to the number of edges,
    so that each edge, labelled with the difference of the labels at its two ends, gets
    a label no other edge has."""
    n_edges = instance["m"]    # the number of edges
    n_nodes = instance["n"]    # the number of nodes
    graph = instance["graph"]  # graph[e] = [u, v]: the two end nodes of edge e

    model = Model()

    # nodes[v] is the label of node v, from 0 to the number of edges
    nodes = [model.intvar(0, n_edges, name=f"node_{v}") for v in range(n_nodes)]
    # edges[e] is the label of edge e, the difference of its end labels, from 1 to the number of edges
    edges = [model.intvar(1, n_edges, name=f"edge_{e}") for e in range(n_edges)]

    # Each edge is labelled with the difference of the labels of its two end nodes.
    for e, (u, v) in enumerate(graph):
        model.distance(nodes[u], nodes[v], "=", edges[e]).post()

    # The edge labels are all different.
    model.all_different(edges).post()
    # The node labels are all different.
    model.all_different(nodes).post()

    return model, {"nodes": nodes, "edges": edges}, None


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
