# csplib_053_graceful_graphs: a PuLP (Python) model from DCP Rosetta.
# Download the `csplib_053_graceful_graphs.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_053_graceful_graphs.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python csplib_053_graceful_graphs.py csplib_053_graceful_graphs.json

import pulp


def create_model(instance):
    """Label the nodes of a graph with m edges with distinct numbers from 0 to m, so
    that the edge labels, the differences between the labels of their end nodes, are
    all different."""
    m = instance["m"]          # the number of edges
    n = instance["n"]          # the number of nodes
    graph = instance["graph"]  # graph[e] = [u, w]: the two end nodes of edge e

    problem = pulp.LpProblem("graceful_graph", pulp.LpMinimize)  # no objective: any labelling that follows the rules will do

    # label[v][value] is 1 when node v gets the label value, and 0 when not
    label = pulp.LpVariable.dicts("label", (range(n), range(m + 1)), cat="Binary")
    # nodes[v] is the label of node v, from 0 to m
    nodes = [pulp.LpVariable(f"nodes_{v}", 0, m, cat="Integer") for v in range(n)]

    # Each node gets exactly one label, and nodes[v] is that label.
    for v in range(n):
        problem += pulp.lpSum(label[v][value] for value in range(m + 1)) == 1
        problem += nodes[v] == pulp.lpSum(value * label[v][value] for value in range(m + 1))

    # Each label from 0 to m goes to at most one node.
    for value in range(m + 1):
        problem += pulp.lpSum(label[v][value] for v in range(n)) <= 1

    # The labels (a, b) of the two end nodes of an edge, with a and b different.
    values = range(m + 1)
    pairs = [(a, b) for a in values for b in values if a != b]
    # ends[e, a, b] is 1 when edge e runs from a node labelled a to a node labelled b.
    ends = {(e, a, b): pulp.LpVariable(f"ends_{e}_{a}_{b}", 0, 1)
            for e in range(m) for (a, b) in pairs}

    # The first end of edge e has the label that starts its chosen pair.
    # The second end of edge e has the label that finishes its chosen pair.
    for e, (u, w) in enumerate(graph):
        for a in values:
            problem += pulp.lpSum(ends[(e, a, b)] for b in values if b != a) == label[u][a]
        for b in values:
            problem += pulp.lpSum(ends[(e, a, b)] for a in values if a != b) == label[w][b]

    # edges[e] is the label of edge e, from 1 to m.
    edges = [pulp.LpVariable(f"edges_{e}", 1, m, cat="Integer") for e in range(m)]
    # The label of each edge is the difference of the labels of its two end nodes.
    for e in range(m):
        problem += edges[e] == pulp.lpSum(abs(a - b) * ends[(e, a, b)] for (a, b) in pairs)

    # The edge labels are all different: there are m edges and m labels from 1 to m,
    # so each label from 1 to m is the label of exactly one edge.
    for d in range(1, m + 1):
        problem += pulp.lpSum(
            ends[(e, a, b)] for e in range(m) for (a, b) in pairs if abs(a - b) == d) == 1

    return problem, {"nodes": nodes, "edges": edges}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
