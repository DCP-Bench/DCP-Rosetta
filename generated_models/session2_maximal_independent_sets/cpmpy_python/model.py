# session2_maximal_independent_sets: a CPMpy model from DCP Rosetta.
# Download the `session2_maximal_independent_sets.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_maximal_independent_sets.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python session2_maximal_independent_sets.py session2_maximal_independent_sets.json

import cpmpy as cp


def create_model(instance):
    """Find a maximal independent set of a graph: a set of nodes, no two of
    them adjacent, that cannot be extended by any further node."""
    adjacency = instance["adjacency_list"]  # adjacency[i]: the nodes (numbered from 1) adjacent to node i+1
    n_nodes = len(adjacency)

    # nodes[i] is true when node i+1 is in the set
    nodes = cp.boolvar(shape=n_nodes, name="nodes")

    model = cp.Model()
    for i, neighbours in enumerate(adjacency):
        # Independent: no two adjacent nodes are both in the set (each edge is listed from both ends).
        for neighbour in neighbours:
            j = neighbour - 1
            if i < j:
                model.add(nodes[i] + nodes[j] <= 1)
        # Maximal: every node is in the set or has a neighbour in it,
        # otherwise it could be added.
        model.add(cp.any([nodes[i]] + [nodes[neighbour - 1] for neighbour in neighbours]))

    return model, {"nodes": nodes}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
