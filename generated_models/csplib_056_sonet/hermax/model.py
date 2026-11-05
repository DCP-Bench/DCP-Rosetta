# csplib_056_sonet: a hermax (Python) model from DCP Rosetta.
# Download the `csplib_056_sonet.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_056_sonet.html
# Then run it on the first instance (after `pip install hermax`):
#   python csplib_056_sonet.py csplib_056_sonet.json

from hermax.model import Model, sum_expr


def create_model(instance):
    """SONET ring design: place each node on some rings (one add-drop multiplexer per
    node and ring it sits on) so that every pair of nodes with traffic between them
    shares at least one ring, no ring holds more nodes than its capacity, and the
    total number of ADMs used is as small as possible."""
    r = instance["r"]                            # number of rings available
    n = instance["n"]                            # number of nodes
    demand = instance["demand"]                  # demand[i][j] > 0: nodes i and j exchange traffic
    capacity_nodes = instance["capacity_nodes"]  # capacity_nodes[k]: most nodes ring k can host

    m = Model()

    # ring_config[k][i] is true when node i is installed on ring k (one ADM there)
    ring_config = m.bool_matrix("ring_config", r, n)

    # Every pair of nodes with traffic between them must share a ring.
    # share[k] is true only when both nodes of the pair are on ring k, and at least
    # one ring must be shared.
    for i in range(n):
        for j in range(i + 1, n):
            if demand[i][j] > 0 or demand[j][i] > 0:
                share = m.bool_vector(f"share_{i}_{j}", r)  # share[k]: nodes i and j both on ring k
                for k in range(r):
                    m &= (~share[k] | ring_config[k][i])
                    m &= (~share[k] | ring_config[k][j])
                m &= share.at_least_one()

    # Each ring hosts at most capacity_nodes[k] nodes.
    for k in range(r):
        m &= (sum(ring_config[k][i] for i in range(n)) <= capacity_nodes[k])

    # The number of ADMs used is the number of node-ring installations.
    adms = sum_expr(ring_config[k][i] for k in range(r) for i in range(n))

    # Minimise the total number of ADMs used.
    m.obj += adms

    # The objective in the problem's terms: the total number of ADMs, the cost minimised above.
    return m, {"ring_config": ring_config, "total_adms": adms}, adms


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
        print("objective =", result[objective])
    else:
        print("No solution:", result.status)
