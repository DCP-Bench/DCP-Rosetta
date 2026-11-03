# csplib_056_sonet: an Exact (Python) model from DCP Rosetta.
# Download the `csplib_056_sonet.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_056_sonet.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python csplib_056_sonet.py csplib_056_sonet.json

from exact import Exact


def create_model(instance):
    """Install nodes on rings, with each install using an add-drop multiplexer (ADM):
    nodes with traffic demand between them must share a ring, a ring hosts a limited
    number of nodes, and the total number of ADMs is as small as possible."""
    n_rings = instance["r"]                # the number of rings
    n_nodes = instance["n"]                # the number of nodes
    demand = instance["demand"]            # demand[i][j] > 0 when nodes i and j exchange traffic
    capacity = instance["capacity_nodes"]  # capacity[k]: the most nodes ring k can host

    solver = Exact()

    # Exact identifies its variables by name.
    # ring_config[k][i] is 1 when node i is installed on ring k, which costs one ADM
    ring_config = [[f"ring_{k}_node_{i}" for i in range(n_nodes)] for k in range(n_rings)]
    for k in range(n_rings):
        for i in range(n_nodes):
            solver.addVariable(ring_config[k][i], 0, 1)

    for i in range(n_nodes):
        for j in range(i + 1, n_nodes):
            if demand[i][j] > 0:
                # carries[k] is 1 when ring k carries the traffic between nodes i and j
                carries = []
                for k in range(n_rings):
                    name = f"ring_{k}_carries_{i}_{j}"
                    solver.addVariable(name, 0, 1)
                    # A ring carries the traffic only when both nodes are on it.
                    solver.addConstraint([(1, ring_config[k][i]), (-1, name)], True, 0)
                    solver.addConstraint([(1, ring_config[k][j]), (-1, name)], True, 0)
                    carries.append((1, name))
                # Nodes i and j with traffic between them share at least one ring.
                solver.addConstraint(carries, True, 1)

    # A ring hosts no more nodes than its capacity.
    for k in range(n_rings):
        solver.addConstraint([(1, name) for name in ring_config[k]], False, 0, True, capacity[k])

    # total_adms is the number of ADMs used, one for each node on a ring.
    solver.addVariable("total_adms", 0, n_rings * n_nodes)
    # every placement of a node on a ring, each costing one ADM
    all_placements = [(1, name) for row in ring_config for name in row]
    solver.addConstraint(all_placements + [(-1, "total_adms")], True, 0, True, 0)

    # Use as few ADMs as possible.
    solver.setObjective(all_placements, minimize=True)

    return solver, {"ring_config": ring_config, "total_adms": "total_adms"}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
