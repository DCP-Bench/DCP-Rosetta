# session2_maximal_independent_sets: a Z3 (Python) model from DCP Rosetta.
# Download the `session2_maximal_independent_sets.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_maximal_independent_sets.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python session2_maximal_independent_sets.py session2_maximal_independent_sets.json

import z3


def create_model(instance):
    """Find a maximal independent set of a graph: a set of nodes, no two of
    them adjacent, that cannot be extended by any further node."""
    adjacency = instance["adjacency_list"]  # adjacency[i]: the nodes (numbered from 1) adjacent to node i+1
    n_nodes = instance["n"]  # the number of nodes in the graph

    # nodes[i] is true when node i+1 is in the set
    nodes = [z3.Bool(f"node_{i}") for i in range(n_nodes)]

    solver = z3.Solver()
    for i, neighbours in enumerate(adjacency):
        # No two adjacent nodes are both in the set. Each edge is listed at both
        # ends, so it is taken once, from its lower end.
        for neighbour in neighbours:
            j = neighbour - 1
            if i < j:
                solver.add(z3.Not(z3.And(nodes[i], nodes[j])))
        # Every node is in the set or next to a node in it, so the set cannot be extended.
        solver.add(z3.Or([nodes[i]] + [nodes[k - 1] for k in neighbours]))

    return solver, {"nodes": nodes}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
