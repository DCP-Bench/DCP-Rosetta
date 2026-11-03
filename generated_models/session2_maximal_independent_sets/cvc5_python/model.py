# session2_maximal_independent_sets: a cvc5 (Python) model from DCP Rosetta.
# Download the `session2_maximal_independent_sets.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_maximal_independent_sets.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python session2_maximal_independent_sets.py session2_maximal_independent_sets.json

import cvc5.pythonic as c5


def create_model(instance):
    """Find a maximal independent set of a graph: a set of nodes, no two of
    them adjacent, such that every node outside the set is adjacent to a node
    in it."""
    n_nodes = instance["n"]                      # the number of nodes
    adjacency_list = instance["adjacency_list"]  # adjacency_list[i]: the nodes next to node i+1

    # nodes[i] is true when node i+1 is in the set
    nodes = [c5.Bool(f"node_{i}") for i in range(n_nodes)]

    solver = c5.Solver()

    for i, neighbours in enumerate(adjacency_list):
        # No two adjacent nodes are both in the set.
        for j in neighbours:
            solver.add(c5.Not(c5.And(nodes[i], nodes[j - 1])))

        # Node i+1 is in the set, or one of its neighbours is, so it cannot be added.
        cover = [nodes[j - 1] for j in neighbours]
        if not cover:
            solver.add(nodes[i])
        elif len(cover) == 1:
            solver.add(c5.Or(nodes[i], cover[0]))
        else:
            solver.add(c5.Or(nodes[i], c5.Or(cover)))

    return solver, {"nodes": nodes}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
