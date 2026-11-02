# csplib_056_sonet: a PuLP (Python) model from DCP Rosetta.
# Download the `csplib_056_sonet.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_056_sonet.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python csplib_056_sonet.py csplib_056_sonet.json

import pulp


def create_model(instance):
    """Install nodes on rings, with each installation using one add-drop multiplexer
    (ADM). Two nodes that communicate must share a ring, and a ring can host only so
    many nodes. Use as few ADMs as possible."""
    r = instance["r"]                      # the number of rings
    n = instance["n"]                      # the number of nodes
    demand = instance["demand"]            # demand[i][j] > 0: nodes i and j communicate
    capacity = instance["capacity_nodes"]  # capacity[k]: the most nodes ring k can host

    rings, nodes = range(r), range(n)
    problem = pulp.LpProblem("sonet", pulp.LpMinimize)

    # on_ring[k][i] is 1 when node i is installed on ring k, and 0 when not
    on_ring = [[pulp.LpVariable(f"ring_{k}_{i}", cat="Binary") for i in nodes] for k in rings]

    # Each pair of nodes that communicate shares a ring.
    for i in nodes:
        for j in nodes:
            if j <= i or demand[i][j] <= 0:
                continue
            # both[k] is 1 exactly when nodes i and j are both installed on ring k
            both = []
            for k in rings:
                b = pulp.LpVariable(f"both_{i}_{j}_{k}", cat="Binary")
                problem += b <= on_ring[k][i]
                problem += b <= on_ring[k][j]
                problem += b >= on_ring[k][i] + on_ring[k][j] - 1
                both.append(b)
            problem += pulp.lpSum(both) >= 1

    # Each ring hosts no more nodes than its capacity.
    for k in rings:
        problem += pulp.lpSum(on_ring[k]) <= capacity[k]

    # Each node installed on a ring takes one ADM, and the total is minimized.
    adms = pulp.lpSum(on_ring[k][i] for k in rings for i in nodes)
    problem += adms

    return problem, {"ring_config": on_ring, "total_adms": adms}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
