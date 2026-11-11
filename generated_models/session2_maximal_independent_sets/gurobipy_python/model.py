# session2_maximal_independent_sets: a Gurobi (Python) model from DCP Rosetta.
# Download the `session2_maximal_independent_sets.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_maximal_independent_sets.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python session2_maximal_independent_sets.py session2_maximal_independent_sets.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Choose nodes of a graph so that no two chosen nodes are adjacent and every other node is adjacent to a chosen one, so that no further node can be added."""
    neighbours = instance["adjacency_list"]  # neighbours[i] lists the nodes adjacent to node i+1 (the data numbers nodes from 1)
    vertices = range(instance["n"])  # node i+1 is the i-th of the n nodes

    model = gp.Model("maximal_independent_sets")

    # nodes[i] is 1 when node i+1 is in the set, and 0 when not
    nodes = model.addVars(vertices, vtype=GRB.BINARY, name="nodes")

    # Independence: no two adjacent nodes are both in the set. Each edge is written once, from its
    # lower-numbered end (k - 1 is the neighbour's index).
    model.addConstrs((nodes[i] + nodes[k - 1] <= 1
                      for i in vertices for k in neighbours[i] if i < k - 1), name="independent")

    # Maximality: every node is in the set or has a neighbour in it.
    model.addConstrs((nodes[i] + gp.quicksum(nodes[k - 1] for k in neighbours[i]) >= 1
                      for i in vertices), name="maximal")

    # No objective: any set that meets these constraints is a solution.
    return model, {"nodes": [nodes[i] for i in vertices]}


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
