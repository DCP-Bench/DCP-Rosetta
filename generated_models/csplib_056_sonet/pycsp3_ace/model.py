# csplib_056_sonet: a PyCSP3 model from DCP Rosetta.
# Download the `csplib_056_sonet.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_056_sonet.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python csplib_056_sonet.py csplib_056_sonet.json

from pycsp3 import *


def create_model(instance):
    """Install the nodes of a SONET network on rings, using an add-drop multiplexer
    (ADM) for each node on each ring it is installed on. Each ring can host only a
    given number of nodes, and two nodes with traffic between them must be on at
    least one common ring. Minimise the total number of ADMs."""
    n_nodes = instance["n"]                       # number of nodes
    n_rings = instance["r"]                       # number of rings
    capacity_nodes = instance["capacity_nodes"]   # capacity_nodes[k] is the most nodes ring k can host
    demand = instance["demand"]                   # demand[i][j] is the traffic between nodes i and j, 0 when there is none

    # The pairs of nodes (i, j), i < j, that have traffic between them in either direction.
    pairs = [(i, j) for i in range(n_nodes) for j in range(i + 1, n_nodes) if demand[i][j] or demand[j][i]]

    # ring_config[k][i] is 1 when node i is on ring k, 0 otherwise.
    ring_config = VarArray(size=[n_rings, n_nodes], dom={0, 1})
    # total_adms is the number of ADMs. A node is on a ring at most once, so there are at most
    # n_rings * n_nodes ADMs.
    total_adms = Var(dom=range(n_rings * n_nodes + 1))

    satisfy(
        # Each ring hosts no more nodes than its capacity.
        [Sum(ring_config[k]) <= capacity_nodes[k] for k in range(n_rings)],
        # Two nodes with traffic between them are both on some common ring.
        [Sum(ring_config[k][i] * ring_config[k][j] for k in range(n_rings)) >= 1 for i, j in pairs],
        # The number of ADMs is the number of nodes installed on rings.
        total_adms == Sum(ring_config),
    )

    # The total number of ADMs is to be as small as possible.
    minimize(total_adms)

    return {"ring_config": ring_config, "total_adms": total_adms}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is OPTIMUM:
        print("ring_config", "=")
        for row in outputs["ring_config"]:
            print(values(row))
    else:
        print("No solution:", status())
