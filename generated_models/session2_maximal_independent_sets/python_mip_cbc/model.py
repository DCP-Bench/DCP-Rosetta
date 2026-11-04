# session2_maximal_independent_sets: a Python-MIP (Python) model from DCP Rosetta.
# Download the `session2_maximal_independent_sets.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_maximal_independent_sets.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python session2_maximal_independent_sets.py session2_maximal_independent_sets.json

import mip


def create_model(instance):
    """Find a maximal independent set of a graph: a set of nodes, no two of
    them adjacent, such that every node outside the set is adjacent to a node in it."""
    n_nodes = instance["n"]  # the number of nodes, numbered from 1
    adjacency_list = instance["adjacency_list"]  # adjacency_list[i]: the nodes adjacent to node i+1

    model = mip.Model(solver_name="CBC")

    # nodes[i] is 1 when node i+1 is in the set, and 0 otherwise
    nodes = [model.add_var(f"nodes_{i}", var_type=mip.BINARY) for i in range(n_nodes)]

    for i, neighbours in enumerate(adjacency_list):
        # No two adjacent nodes are both in the set.
        for neighbour in neighbours:
            model.add_constr(nodes[i] + nodes[neighbour - 1] <= 1)
        # The node is in the set or next to a node in it, so it cannot be added to the set.
        model.add_constr(nodes[i] + mip.xsum(nodes[neighbour - 1] for neighbour in neighbours) >= 1)

    return model, {"nodes": nodes}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
