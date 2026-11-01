# csplib_056_sonet: a Choco-solver (Python) model from DCP Rosetta.
# Download the `csplib_056_sonet.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_056_sonet.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python csplib_056_sonet.py csplib_056_sonet.json

from pychoco.model import Model


def create_model(instance):
    """Install nodes on rings, each installation using one add-drop multiplexer (ADM), so
    that nodes which communicate share a ring, no ring holds more nodes than its capacity,
    and the total number of ADMs is as small as possible."""
    n_rings = instance["r"]                      # the number of rings
    n_nodes = instance["n"]                      # the number of nodes
    demand = instance["demand"]                  # demand[i][j] > 0: nodes i and j communicate
    capacity_nodes = instance["capacity_nodes"]  # capacity_nodes[k]: the most nodes ring k can host

    model = Model()

    # ring_config[k][i] is true when node i is installed on ring k
    ring_config = [
        [model.boolvar(name=f"ring_config_{k}_{i}") for i in range(n_nodes)]
        for k in range(n_rings)
    ]

    # Nodes i and j that communicate share at least one ring.
    for i in range(n_nodes):
        for j in range(i + 1, n_nodes):
            if demand[i][j] > 0:
                # both_on[k] is true when nodes i and j are both installed on ring k
                both_on = [
                    model.sum([ring_config[k][i], ring_config[k][j]], ">=", 2).reify()
                    for k in range(n_rings)
                ]
                model.sum(both_on, ">=", 1).post()

    # Each ring hosts no more nodes than its capacity.
    for k in range(n_rings):
        model.sum(ring_config[k], "<=", capacity_nodes[k]).post()

    # total_adms is the number of ADMs in use, one for each node installed on a ring.
    total_adms = model.intvar(0, n_rings * n_nodes, name="total_adms")
    model.sum([ring_config[k][i] for k in range(n_rings) for i in range(n_nodes)], "=", total_adms).post()

    # Minimise the number of ADMs.
    return model, {"ring_config": ring_config, "total_adms": total_adms}, {"objective": total_adms, "maximize": False}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
