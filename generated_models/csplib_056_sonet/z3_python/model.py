# csplib_056_sonet: a Z3 (Python) model from DCP Rosetta.
# Download the `csplib_056_sonet.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_056_sonet.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python csplib_056_sonet.py csplib_056_sonet.json

import z3


def create_model(instance):
    """Install nodes on rings, with each installation using an add-drop multiplexer
    (ADM): nodes with traffic between them must share a ring, a ring hosts a limited
    number of nodes, and the total number of ADMs is as small as possible."""
    r = instance["r"]                           # the number of rings
    n = instance["n"]                           # the number of nodes
    demand = instance["demand"]                 # demand[i][j] > 0: nodes i and j communicate
    capacity_nodes = instance["capacity_nodes"] # capacity_nodes[k]: the most nodes ring k can host

    # ring_config[k][i] is true when node i is installed on ring k
    ring_config = [[z3.Bool(f"ring_config_{k}_{i}") for i in range(n)] for k in range(r)]
    # total_adms is the number of ADMs used, one for each node installed on a ring
    total_adms = z3.Int("total_adms")

    solver = z3.Optimize()
    # Two nodes with traffic between them share at least one ring.
    for i in range(n):
        for j in range(i + 1, n):
            if demand[i][j] > 0:
                solver.add(z3.Or([z3.And(ring_config[k][i], ring_config[k][j])
                                  for k in range(r)]))

    # No ring holds more nodes than its capacity.
    for k in range(r):
        solver.add(z3.PbLe([(ring_config[k][i], 1) for i in range(n)], capacity_nodes[k]))

    # Each node installed on a ring costs one ADM.
    solver.add(total_adms == z3.Sum([z3.If(ring_config[k][i], 1, 0)
                                     for k in range(r) for i in range(n)]))

    # Minimise the total number of ADMs.
    solver.minimize(total_adms)

    return solver, {"ring_config": ring_config, "total_adms": total_adms}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
