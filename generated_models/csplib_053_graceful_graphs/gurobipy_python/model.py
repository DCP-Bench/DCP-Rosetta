# csplib_053_graceful_graphs: a Gurobi (Python) model from DCP Rosetta.
# Download the `csplib_053_graceful_graphs.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_053_graceful_graphs.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python csplib_053_graceful_graphs.py csplib_053_graceful_graphs.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Label the nodes of a graph with q edges by distinct whole numbers from 0 to q, so that the edge labels, the differences between the labels of their end nodes, are all different (a graceful labelling)."""
    m = instance["m"]  # q, the number of edges
    n = instance["n"]  # the number of nodes
    graph = instance["graph"]  # graph[e] = [x, y]: the two end nodes of edge e
    node_labels = range(m + 1)  # the node labels 0 to q
    edge_labels = range(1, m + 1)  # the edge labels 1 to q (the range is implied by the node labels, not stated)

    model = gp.Model("graceful_graphs")

    # node_is[i, a] is 1 when node i gets label a.
    node_is = model.addVars(n, node_labels, vtype=GRB.BINARY, name="node_is")
    # Each node gets exactly one label.
    model.addConstrs((node_is.sum(i, "*") == 1 for i in range(n)), name="node_label")
    # No two nodes share a label.
    model.addConstrs((node_is.sum("*", a) <= 1 for a in node_labels), name="node_distinct")
    # nodes[i] is the label of node i.
    nodes = [gp.quicksum(a * node_is[i, a] for a in node_labels) for i in range(n)]

    # edge_is[e, d] is 1 when edge e gets label d.
    edge_is = model.addVars(m, edge_labels, vtype=GRB.BINARY, name="edge_is")
    # Each edge gets exactly one label.
    model.addConstrs((edge_is.sum(e, "*") == 1 for e in range(m)), name="edge_label")
    # The edge labels are all different.
    model.addConstrs((edge_is.sum("*", d) <= 1 for d in edge_labels), name="edge_distinct")
    # edges[e] is the label of edge e.
    edges = [gp.quicksum(d * edge_is[e, d] for d in edge_labels) for e in range(m)]

    # The label of edge e is |f(x) - f(y)|, where x and y are its end nodes. gp.abs_ takes
    # a variable, so the signed difference gets a variable of its own; it lies in -q..q
    # because the node labels do.
    for e, (x, y) in enumerate(graph):
        diff = model.addVar(lb=-m, ub=m, vtype=GRB.INTEGER, name=f"diff[{e}]")
        size = model.addVar(lb=0, ub=m, vtype=GRB.INTEGER, name=f"size[{e}]")
        model.addConstr(diff == nodes[x] - nodes[y], name=f"diff_def[{e}]")
        model.addConstr(size == gp.abs_(diff), name=f"abs[{e}]")
        model.addConstr(size == edges[e], name=f"edge_value[{e}]")

    return model, {"nodes": nodes, "edges": edges}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.Params.OutputFlag = 0  # no solver log
    model.optimize()

    if model.Status == GRB.OPTIMAL:  # a solution
        # a variable's value is var.X, an expression's is expr.getValue(); both read through LinExpr
        value = np.vectorize(lambda out: round(gp.LinExpr(out).getValue()))
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution, Gurobi status", model.Status)  # 3 infeasible, 4 infeasible or unbounded
