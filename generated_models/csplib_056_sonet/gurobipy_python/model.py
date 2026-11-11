# csplib_056_sonet: a Gurobi (Python) model from DCP Rosetta.
# Download the `csplib_056_sonet.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_056_sonet.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python csplib_056_sonet.py csplib_056_sonet.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Place n nodes on r rings so that every pair of nodes with traffic between them shares a ring, no ring holds more nodes than its capacity, and the total number of add-drop multiplexers (one per node on each ring it is on) is as small as possible."""
    r = instance["r"]  # the number of rings, numbered 0 to r-1
    n = instance["n"]  # the number of nodes, numbered 0 to n-1
    demand = instance["demand"]  # demand[i][j]: the traffic between nodes i and j, 0 when none
    capacity = instance["capacity_nodes"]  # capacity[k]: the most nodes that ring k can host
    rings = range(r)
    nodes = range(n)
    # The pairs of nodes with traffic between them in either direction, each listed once with i < j.
    talking = [(i, j) for i in nodes for j in range(i + 1, n) if demand[i][j] > 0 or demand[j][i] > 0]

    model = gp.Model("sonet")

    # ring_config[k, i] is 1 when node i is installed on ring k, which takes one ADM.
    ring_config = model.addVars(rings, nodes, vtype=GRB.BINARY, name="ring_config")

    # together[k, i, j] is an auxiliary variable for a pair (i, j) with traffic: it can be 1 only
    # when both i and j are on ring k. The demand constraints below force it to 1 on some ring.
    together = model.addVars([(k, i, j) for k in rings for (i, j) in talking], vtype=GRB.BINARY,
                             name="together")
    # A pair can share ring k only if node i is on ring k ...
    model.addConstrs((together[k, i, j] <= ring_config[k, i] for k, i, j in together), name="on_ring_i")
    # ... and only if node j is on ring k.
    model.addConstrs((together[k, i, j] <= ring_config[k, j] for k, i, j in together), name="on_ring_j")

    # Two nodes with traffic between them share at least one ring.
    model.addConstrs((gp.quicksum(together[k, i, j] for k in rings) >= 1 for i, j in talking),
                     name="demand")

    # Ring k holds no more nodes than its capacity (ring_config.sum(k, "*") adds over the nodes).
    model.addConstrs((ring_config.sum(k, "*") <= capacity[k] for k in rings), name="capacity")

    # Objective: minimise the total number of ADMs, one per node on each ring (the sum of ring_config).
    total_adms = ring_config.sum()
    model.setObjective(total_adms, GRB.MINIMIZE)

    return model, {"ring_config": [[ring_config[k, i] for i in nodes] for k in rings],
                   "total_adms": total_adms}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.Params.OutputFlag = 0  # no solver log
    model.Params.MIPGap = 0  # prove the optimum; the default stops within 0.01% of it
    model.optimize()

    if model.Status == GRB.OPTIMAL:  # a proven optimum
        print("Objective value:", round(model.ObjVal))
        # a variable's value is var.X, an expression's is expr.getValue(); both read through LinExpr
        value = np.vectorize(lambda out: round(gp.LinExpr(out).getValue()))
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution, Gurobi status", model.Status)  # 3 infeasible, 4 infeasible or unbounded
