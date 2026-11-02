# session2_maximal_independent_sets: an Exact (Python) model from DCP Rosetta.
# Download the `session2_maximal_independent_sets.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_maximal_independent_sets.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python session2_maximal_independent_sets.py session2_maximal_independent_sets.json

from exact import Exact


def create_model(instance):
    """Find a maximal independent set of a graph: a set of nodes, no two of
    them adjacent, such that every node outside the set is adjacent to a node in it."""
    n_nodes = instance["n"]                       # the number of nodes
    adjacency_list = instance["adjacency_list"]  # adjacency_list[i]: the nodes adjacent to node i+1

    solver = Exact()

    # Exact identifies its variables by name.
    # nodes[i] is 1 when node i+1 is in the set, and 0 when not.
    nodes = [f"node_{i}" for i in range(n_nodes)]
    for name in nodes:
        solver.addVariable(name, 0, 1)

    for i, neighbours in enumerate(adjacency_list):
        for neighbour in neighbours:
            j = neighbour - 1
            if i < j:
                # Two adjacent nodes are not both in the set.
                solver.addConstraint([(1, nodes[i]), (1, nodes[j])], False, 0, True, 1)

    for i, neighbours in enumerate(adjacency_list):
        # Every node is in the set or next to a node in the set, so no node can be added.
        solver.addConstraint([(1, nodes[i])] + [(1, nodes[neighbour - 1]) for neighbour in neighbours],
                             True, 1)

    return solver, {"nodes": nodes}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
