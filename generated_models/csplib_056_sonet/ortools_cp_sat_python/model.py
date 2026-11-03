# csplib_056_sonet: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `csplib_056_sonet.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_056_sonet.html
# Then run it on the first instance (after `pip install ortools`):
#   python csplib_056_sonet.py csplib_056_sonet.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Install nodes on rings, with each install using an add-drop multiplexer (ADM):
    nodes with traffic demand between them must share a ring, a ring hosts a limited
    number of nodes, and the total number of ADMs is as small as possible."""
    n_rings = instance["r"]                # the number of rings
    n_nodes = instance["n"]                # the number of nodes
    demand = instance["demand"]            # demand[i][j] > 0: nodes i and j communicate
    capacity = instance["capacity_nodes"]  # capacity[k]: the most nodes ring k can host

    model = cp_model.CpModel()

    # ring_config[k][i] is true when node i is installed on ring k (one ADM)
    ring_config = [
        [model.new_bool_var(f"ring_{k}_{i}") for i in range(n_nodes)] for k in range(n_rings)
    ]

    # Nodes i and j with traffic between them share at least one ring.
    for i in range(n_nodes):
        for j in range(i + 1, n_nodes):
            if demand[i][j] <= 0:
                continue
            # both[k] is true when nodes i and j are both installed on ring k
            both = []
            for k in range(n_rings):
                shared = model.new_bool_var(f"both_{i}_{j}_{k}")
                model.add_bool_and([ring_config[k][i], ring_config[k][j]]).only_enforce_if(shared)
                model.add_bool_or([~ring_config[k][i], ~ring_config[k][j]]).only_enforce_if(~shared)
                both.append(shared)
            model.add_bool_or(both)

    # A ring hosts no more nodes than its capacity.
    for k in range(n_rings):
        model.add(sum(ring_config[k]) <= capacity[k])

    # Each node installed on a ring takes one ADM. Minimize the total.
    n_adms = sum(ring_config[k][i] for k in range(n_rings) for i in range(n_nodes))
    model.minimize(n_adms)

    return model, {"ring_config": ring_config, "total_adms": n_adms}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
