from hermax.model import Model


def build(instance):
    m = instance["m"]  # number of edges
    n = instance["n"]  # number of nodes
    graph = instance["graph"]  # edges as list of [u, v]

    model = Model()

    # Assign each node a unique label from 0 to m (q edges means labels 0..q)
    node_labels = model.int_vector("node_labels", n, 0, m)

    # All node labels must be unique
    model &= node_labels.all_different()

    # Compute edge labels: for each edge (u, v), label is |node_labels[u] - node_labels[v]|
    # We create edge_labels as integer variables and constrain them to be the absolute differences
    edge_labels = model.int_vector("edge_labels", m, 1, m)

    # All edge labels must be different
    model &= edge_labels.all_different()

    # For each edge, ensure the label equals the absolute difference of its endpoints
    for i, (u, v) in enumerate(graph):
        # The edge label is the absolute difference: |node_labels[u] - node_labels[v]|
        # Create auxiliary IntVar for the two possible differences, then take max
        diff_uv = model.int(f"diff_uv_{i}", -m, m)
        diff_vu = model.int(f"diff_vu_{i}", -m, m)

        # Constrain the auxiliary variables to be the differences
        model &= (diff_uv == node_labels[u] - node_labels[v])
        model &= (diff_vu == node_labels[v] - node_labels[u])

        # Use model.max() to compute the absolute value
        abs_diff = model.max([diff_uv, diff_vu])
        model &= (edge_labels[i] == abs_diff)

    return model, {
        "nodes": node_labels,
        "edges": edge_labels
    }
