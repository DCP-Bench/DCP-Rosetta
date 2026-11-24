# csplib_053_graceful_graphs: a CPLEX (Python) model from DCP Rosetta.
# Download the `csplib_053_graceful_graphs.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_053_graceful_graphs.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python csplib_053_graceful_graphs.py csplib_053_graceful_graphs.json

from docplex.mp.model import Model


def create_model(instance):
    """Graceful graph labelling: label the n nodes of a graph with m edges by different numbers in
    0..m so that the edge labels, each the absolute difference of its two end labels, are the
    different numbers 1..m."""
    m = instance["m"]          # number of edges
    n = instance["n"]          # number of nodes
    graph = instance["graph"]  # graph[k] = [u, v]: the end nodes of edge k

    model = Model("graceful_graphs")

    # node_has[i, a] is 1 when node i carries label a in 0..m. Each node has one label and no
    # label is used twice, so the node labels are all different.
    node_has = {(i, a): model.binary_var(name=f"node_{i}_{a}") for i in range(n) for a in range(m + 1)}
    model.add_constraints(model.sum(node_has[i, a] for a in range(m + 1)) == 1 for i in range(n))
    model.add_constraints(model.sum(node_has[i, a] for i in range(n)) <= 1 for a in range(m + 1))
    # nodes[i] is the label of node i.
    nodes = [model.sum(a * node_has[i, a] for a in range(m + 1)) for i in range(n)]

    # edge_has[k, d] is 1 when edge k carries label d. Different nodes have different labels in
    # 0..m, so an edge label is at least 1 and at most m. Each edge has one label and no
    # label is used twice, so the edge labels are all different.
    edge_has = {(k, d): model.binary_var(name=f"edge_{k}_{d}") for k in range(m) for d in range(1, m + 1)}
    model.add_constraints(model.sum(edge_has[k, d] for d in range(1, m + 1)) == 1 for k in range(m))
    model.add_constraints(model.sum(edge_has[k, d] for k in range(m)) <= 1 for d in range(1, m + 1))
    # edges[k] is the label of edge k, in the order of the edges in graph.
    edges = [model.sum(d * edge_has[k, d] for d in range(1, m + 1)) for k in range(m)]

    # The label of each edge is the absolute difference of the labels of its end nodes:
    # upward[k] is 1 when the second end carries the larger label.
    for k, (u, v) in enumerate(graph):
        upward = model.binary_var(name=f"upward_{k}")
        model.add_indicator(upward, nodes[v] - nodes[u] == edges[k], active_value=1)
        model.add_indicator(upward, nodes[u] - nodes[v] == edges[k], active_value=0)

    return model, {"nodes": nodes, "edges": edges}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solution = model.solve()

    if solution:  # a solution
        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
