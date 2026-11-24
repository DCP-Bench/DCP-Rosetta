# csplib_056_sonet: a CPLEX (Python) model from DCP Rosetta.
# Download the `csplib_056_sonet.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_056_sonet.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python csplib_056_sonet.py csplib_056_sonet.json

from docplex.mp.model import Model


def create_model(instance):
    """SONET: put nodes on rings so every pair with traffic shares a ring, within ring capacities, with the fewest ADMs."""
    r = instance["r"]                      # number of rings
    n = instance["n"]                      # number of nodes
    demand = instance["demand"]            # demand[i][j] is positive when nodes i and j must communicate
    capacity = instance["capacity_nodes"]  # capacity[k]: the most nodes ring k can host
    rings = range(r)
    nodes = range(n)
    # The pairs of nodes that must communicate, each pair listed once.
    talking = [(i, j) for i in nodes for j in range(i + 1, n) if demand[i][j] > 0]

    model = Model("sonet")

    # ring_config[k, i] is 1 when node i is installed on ring k (one ADM).
    ring_config = model.binary_var_matrix(rings, nodes, name="ring_config")

    # together[k, i, j] can be 1 only when nodes i and j are both on ring k.
    together = {(k, i, j): model.binary_var(name=f"together_{k}_{i}_{j}") for k in rings for (i, j) in talking}
    for (k, i, j), both in together.items():
        model.add_constraint(both <= ring_config[k, i], ctname=f"on_ring_i_{k}_{i}_{j}")
        model.add_constraint(both <= ring_config[k, j], ctname=f"on_ring_j_{k}_{i}_{j}")

    # Two nodes with traffic between them share at least one ring.
    model.add_constraints(model.sum(together[k, i, j] for k in rings) >= 1 for (i, j) in talking)

    # No ring hosts more nodes than its capacity.
    model.add_constraints(model.sum(ring_config[k, i] for i in nodes) <= capacity[k] for k in rings)

    # Minimise the number of ADMs, one per node on a ring.
    total_adms = model.sum(ring_config.values())
    model.minimize(total_adms)

    return model, {"ring_config": [[ring_config[k, i] for i in nodes] for k in rings],
                   "total_adms": total_adms}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.parameters.mip.tolerances.mipgap = 0  # prove the optimum; the default stops within 0.01% of it
    solution = model.solve()

    if solution:  # a proven optimum
        print("Objective value:", round(solution.objective_value))

        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
