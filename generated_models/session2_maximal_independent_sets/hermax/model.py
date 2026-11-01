from hermax.model import Model


def build(instance):
    n = instance["n"]
    adjacency = instance["adjacency_list"]  # 1-based neighbour ids

    m = Model()
    nodes = m.bool_vector("node", n)

    # Independence: no two adjacent nodes are both in the set.
    for i in range(n):
        for j in adjacency[i]:
            k = j - 1
            if k > i:
                m &= (~nodes[i] | ~nodes[k])

    # Maximality: every node outside the set has a neighbour inside it,
    # so the set cannot be extended by adding a node.
    for i in range(n):
        neighbours = [nodes[j - 1] for j in adjacency[i]]
        clause = nodes[i]
        for lit in neighbours:
            clause = clause | lit
        m &= clause

    return m, {"nodes": nodes}
