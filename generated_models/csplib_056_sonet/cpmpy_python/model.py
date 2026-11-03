# csplib_056_sonet: a CPMpy model from DCP Rosetta.
# Download the `csplib_056_sonet.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_056_sonet.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python csplib_056_sonet.py csplib_056_sonet.json

import cpmpy as cp


def create_model(instance):
    """Install nodes on rings, with each install using an add-drop multiplexer (ADM):
    nodes with traffic demand between them must share a ring, a ring hosts a limited
    number of nodes, and the total number of ADMs is as small as possible."""
    rings = instance["r"]                # the number of rings
    nodes = instance["n"]                # the number of nodes
    demand = instance["demand"]          # demand[i][j] > 0: nodes i and j communicate
    capacity = instance["capacity_nodes"]  # capacity[k]: the most nodes ring k can host

    # ring_config[k, i] is true when node i is installed on ring k (one ADM)
    ring_config = cp.boolvar(shape=(rings, nodes), name="ring_config")
    # total_adms is the number of ADMs used, one per node installed on a ring
    total_adms = cp.intvar(0, rings * nodes, name="total_adms")

    model = cp.Model()
    # Two nodes with traffic demand between them share at least one ring.
    for i in range(nodes):
        for j in range(i + 1, nodes):
            if demand[i][j] > 0:
                model.add(cp.any(ring_config[:, i] & ring_config[:, j]))
    # Each ring hosts no more nodes than its capacity.
    for k in range(rings):
        model.add(cp.sum(ring_config[k]) <= capacity[k])
    # Count the ADMs.
    model.add(total_adms == cp.sum(ring_config))
    # Use as few ADMs as possible.
    model.minimize(total_adms)

    return model, {"ring_config": ring_config, "total_adms": total_adms}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
