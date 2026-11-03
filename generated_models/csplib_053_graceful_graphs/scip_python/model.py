# csplib_053_graceful_graphs: a SCIP (Python) model from DCP Rosetta.
# Download the `csplib_053_graceful_graphs.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_053_graceful_graphs.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python csplib_053_graceful_graphs.py csplib_053_graceful_graphs.json

from pyscipopt import Model


def create_model(instance):
    """Graceful labelling of a graph with n nodes and m edges.

    Each node gets a label from 0 to m, and no two nodes share a label. Each
    edge xy is then labelled with the difference |f(x) - f(y)| of its end labels.
    The graph is graceful when all m edge labels are different. The edge labels
    then fill 1 to m exactly, because each lies in that range and none is 0
    (equal end labels are excluded by the distinct node labels).

    Returns (model, outputs), where outputs["nodes"] holds the node labels and
    outputs["edges"] the edge labels.
    """
    n = instance["n"]  # number of nodes, numbered 0 to n-1
    m = instance["m"]  # number of edges; graph lists them in order, 0 to m-1
    graph = instance["graph"]  # graph[j] = [u, v]: edge j joins nodes u and v (0-based)

    model = Model("graceful_graph")

    # Label values, from the statement: node labels are 0 to m, edge labels are 1 to m.
    values = list(range(m + 1))

    # node_label_is[v, k] is 1 when node v has label k, for the m + 1 labels 0 to m.
    # Each node has exactly one label, so each row sums to 1.
    node_label_is = model.addMatrixVar((n, m + 1), vtype="B", name="node_label_is")
    model.addMatrixCons(node_label_is.sum(axis=1) == 1)
    # Node labels are all different: each label is given to at most one node. SCIP
    # has no all-different constraint, so this "at most once per value" stands in for it.
    model.addMatrixCons(node_label_is.sum(axis=0) <= 1)
    node_label = node_label_is @ values  # node_label[v]: the label of node v

    # edge_label_is[j, k] is 1 when edge j has label k. Label 0 is switched off by
    # the upper bound: an edge label is a difference of two distinct node labels,
    # so it is never 0.
    edge_label_is = model.addMatrixVar(
        (m, m + 1), vtype="B", ub=[[0] + [1] * m for _ in range(m)], name="edge_label_is"
    )
    model.addMatrixCons(edge_label_is.sum(axis=1) == 1)
    # Edge labels are all different, the same one-hot "at most once per value" as for the nodes.
    model.addMatrixCons(edge_label_is.sum(axis=0) <= 1)
    edge_label = edge_label_is @ values  # edge_label[j]: the label of edge j

    # sign[j] is 1 when the first end of edge j has the larger label, and 0 when the
    # second end has it. This sign binary replaces an absolute value, because abs is
    # slow in SCIP. The order is forced by the edge labels being at least 1 (see edge_label_is).
    sign = [model.addVar(name=f"sign_{j}", vtype="B") for j in range(m)]

    # Each edge label is the difference of its end labels, in the order the sign gives.
    # An equality is written as two indicators, because addConsIndicator takes no equality.
    for j, (u, v) in enumerate(graph):
        model.addConsIndicator(edge_label[j] - (node_label[u] - node_label[v]) <= 0, binvar=sign[j])
        model.addConsIndicator(edge_label[j] - (node_label[u] - node_label[v]) >= 0, binvar=sign[j])
        model.addConsIndicator(
            edge_label[j] - (node_label[v] - node_label[u]) <= 0, binvar=sign[j], activeone=False
        )
        model.addConsIndicator(
            edge_label[j] - (node_label[v] - node_label[u]) >= 0, binvar=sign[j], activeone=False
        )

    # The problem has no objective: any labelling that meets the constraints is an answer.
    outputs = {"edges": edge_label, "nodes": node_label}
    return model, outputs


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
