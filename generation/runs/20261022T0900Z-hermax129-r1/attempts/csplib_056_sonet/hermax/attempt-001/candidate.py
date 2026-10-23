from hermax.model import Model


def build(instance):
    """
    SONET problem: minimize total ADMs while satisfying communication demands.

    Each ring k can host up to capacity_nodes[k] nodes.
    For two nodes to communicate, they must be on at least one common ring.
    An ADM is an add-drop multiplexer, one per node on a ring.
    Objective: minimize the total number of ADMs.
    """
    r = instance["r"]  # number of rings
    n = instance["n"]  # number of nodes
    demand = instance["demand"]  # n x n demand matrix
    capacity_nodes = instance["capacity_nodes"]  # capacity of each ring

    m = Model()

    # ring_config[k][i] = True if node i is on ring k
    ring_config = m.bool_matrix("ring_config", r, n)

    # Constraint 1: Each ring k can have at most capacity_nodes[k] nodes
    for k in range(r):
        m &= (sum(ring_config[k, i] for i in range(n)) <= capacity_nodes[k])

    # Constraint 2: For each demand pair (i, j), nodes i and j must be on at least one common ring
    for i in range(n):
        for j in range(i + 1, n):
            if demand[i][j] > 0:
                # At least one ring k must have both i and j
                # Create auxiliary booleans for each ring to track if both nodes are on it
                common_rings = []
                for k in range(r):
                    common_k = m.bool(f"common_{i}_{j}_{k}")
                    # Encode: common_k <=> (ring_config[k, i] & ring_config[k, j])
                    # Forward: common_k => ring_config[k, i] & ring_config[k, j]
                    m &= (~common_k | ring_config[k, i])
                    m &= (~common_k | ring_config[k, j])
                    # Backward: ring_config[k, i] & ring_config[k, j] => common_k
                    m &= (~ring_config[k, i] | ~ring_config[k, j] | common_k)
                    common_rings.append(common_k)
                # At least one ring must have both
                m &= (sum(common_rings) >= 1)

    # Objective: minimize total ADMs (soft clauses pay for each placement)
    # According to hermax: to minimize a total, pay when the literal is TRUE
    # So we use ~(negation) to pay when ring_config is TRUE
    for k in range(r):
        for i in range(n):
            m.obj[1] += ~ring_config[k, i]

    # Calculate total_adms
    total_adms = sum(ring_config[k, i] for k in range(r) for i in range(n))

    return m, {"ring_config": ring_config, "total_adms": total_adms}
