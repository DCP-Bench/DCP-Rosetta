# csplib_056_sonet: a SCIP (Python) model from DCP Rosetta.
# Download the `csplib_056_sonet.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_056_sonet.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python csplib_056_sonet.py csplib_056_sonet.json

import numpy as np
from pyscipopt import Model, quicksum


def create_model(instance):
    """SONET ring assignment: each node is installed on some of the rings by an
    add-drop multiplexer (one ADM per node and ring), each ring hosts at most a
    given number of nodes, and every two nodes with traffic demand between them
    must share a ring. Minimise the total number of ADMs."""
    r = instance["r"]                            # the number of rings, numbered 0..r-1
    n = instance["n"]                            # the number of nodes, numbered 0..n-1
    demand = instance["demand"]                  # demand[i][j]: the traffic between nodes i and j
    capacity_nodes = instance["capacity_nodes"]  # capacity_nodes[k]: the most nodes ring k can host

    model = Model("csplib_056_sonet")

    # x[k, i] is 1 when node i is installed on ring k (one ADM there), and 0 when not
    x = model.addMatrixVar((r, n), vtype="B", name="x")

    # Ring k hosts at most capacity_nodes[k] nodes.
    model.addMatrixCons(x.sum(axis=1) <= np.array(capacity_nodes))

    # Two nodes with traffic between them (in either direction) share at least one ring.
    # For each ring k, shared[k] is 1 when both nodes are on ring k. addConsAnd makes
    # shared[k] equal to the conjunction in both directions, not only "at least".
    for i in range(n):
        for j in range(i + 1, n):
            if demand[i][j] == 0 and demand[j][i] == 0:
                continue
            shared = [model.addVar(vtype="B") for _ in range(r)]
            for k in range(r):
                model.addConsAnd([x[k, i], x[k, j]], shared[k])
            model.addCons(quicksum(shared) >= 1)

    # total_adms counts the ADMs: one for each node on each ring. The objective is this
    # integer variable, tied to the sum.
    # The upper bound r * n follows from counting: each of the n nodes is on at most
    # r rings, one ADM per ring.
    total_adms = model.addVar(vtype="I", lb=0, ub=r * n, name="total_adms")
    model.addCons(total_adms == x.sum())
    model.setObjective(total_adms, "minimize")

    return model, {"ring_config": x, "total_adms": total_adms}


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
