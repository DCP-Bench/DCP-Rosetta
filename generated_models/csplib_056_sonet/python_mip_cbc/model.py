# csplib_056_sonet: a Python-MIP (Python) model from DCP Rosetta.
# Download the `csplib_056_sonet.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_056_sonet.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python csplib_056_sonet.py csplib_056_sonet.json

import mip


def create_model(instance):
    """Install nodes on rings, each installation using an add-drop multiplexer (ADM):
    nodes with traffic between them must share a ring, a ring hosts no more nodes than
    its capacity, and the total number of ADMs is as small as possible."""
    n_rings = instance["r"]                # the number of rings
    n_nodes = instance["n"]                # the number of nodes
    demand = instance["demand"]            # demand[i][j] is the traffic from node i to node j
    capacity = instance["capacity_nodes"]  # capacity[k] is the most nodes ring k can host

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # ring_config[k][i] is 1 when node i is installed on ring k, and 0 when not
    ring_config = [[model.add_var(f"ring_{k}_{i}", var_type=mip.BINARY)
                    for i in range(n_nodes)]
                   for k in range(n_rings)]
    # total_adms is the total number of ADMs used
    total_adms = model.add_var("total_adms", lb=0, ub=n_rings * n_nodes,
                               var_type=mip.INTEGER)

    # Each node installed on a ring takes one ADM.
    model += total_adms == mip.xsum(ring_config[k][i]
                                    for k in range(n_rings) for i in range(n_nodes))

    # Each ring hosts no more nodes than its capacity.
    for k in range(n_rings):
        model += mip.xsum(ring_config[k][i] for i in range(n_nodes)) <= capacity[k]

    # Every pair of nodes with traffic between them is installed on a common ring.
    for i in range(n_nodes):
        for j in range(i + 1, n_nodes):
            if demand[i][j] == 0 and demand[j][i] == 0:
                continue
            # both[k] is 1 when nodes i and j are both installed on ring k, and 0 when not
            both = [model.add_var(f"both_{k}_{i}_{j}", var_type=mip.BINARY)
                    for k in range(n_rings)]
            for k in range(n_rings):
                model += both[k] <= ring_config[k][i]
                model += both[k] <= ring_config[k][j]
            model += mip.xsum(both) >= 1

    # Use as few ADMs as possible.
    model.objective = total_adms

    return model, {"ring_config": ring_config, "total_adms": total_adms}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
