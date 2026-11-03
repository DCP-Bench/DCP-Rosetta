"""SONET: put nodes on rings so that every pair with demand shares a ring, within ring capacities, with the fewest ADMs."""
import hexaly.optimizer as hx


def build(instance):
    # r = number of rings; n = number of nodes; demand[i][j] = traffic demand between nodes i and j
    # (0 means they do not need to communicate); capacity_nodes[k] = most nodes ring k can host
    r, n, demand, capacity = instance["r"], instance["n"], instance["demand"], instance["capacity_nodes"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # ring_config[k][i] = 1 if node i is installed on ring k (one ADM)
    ring_config = [[model.bool() for _ in range(n)] for _ in range(r)]

    # A ring hosts at most its capacity of nodes
    for k in range(r):
        model.constraint(model.sum(ring_config[k]) <= capacity[k])
    # For two nodes to communicate they must be on at least one common ring. Only pairs with a
    # demand in either direction need one. shared[k] = 1 only if both nodes are on ring k; it is
    # kept linear (no product of the two booleans) so Hexaly gets a usable bound
    for i in range(n):
        for j in range(i + 1, n):
            if demand[i][j] or demand[j][i]:
                shared = [model.bool() for _ in range(r)]
                for k in range(r):
                    model.constraint(shared[k] <= ring_config[k][i])
                    model.constraint(shared[k] <= ring_config[k][j])
                model.constraint(model.sum(shared) >= 1)

    # Minimise the total number of ADMs used (one per node installed on a ring)
    total_adms = model.sum(ring_config[k][i] for k in range(r) for i in range(n))
    model.minimize(total_adms)
    return optimizer, {"ring_config": ring_config, "total_adms": total_adms}
