# session2_maximal_independent_sets: a PuLP (Python) model from DCP Rosetta.
# Download the `session2_maximal_independent_sets.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_maximal_independent_sets.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python session2_maximal_independent_sets.py session2_maximal_independent_sets.json

import pulp


def create_model(instance):
    """Find a maximal independent set of a graph: a set of nodes, no two of
    them adjacent, to which no further node can be added."""
    n_nodes = instance["n"]                  # the number of nodes
    adjacency = instance["adjacency_list"]   # adjacency[i]: the nodes next to node i+1

    problem = pulp.LpProblem("maximal_independent_set", pulp.LpMinimize)

    # nodes[i] is 1 when node i+1 is in the set, and 0 when not
    nodes = [pulp.LpVariable(f"node_{i}", cat="Binary") for i in range(n_nodes)]

    for i, neighbours in enumerate(adjacency):
        # No two adjacent nodes are both in the set (each pair is added once).
        for neighbour in neighbours:
            j = neighbour - 1
            if i < j:
                problem += nodes[i] + nodes[j] <= 1

        # Every node is in the set or next to a node in it, so no node can be added.
        problem += nodes[i] + pulp.lpSum(nodes[k - 1] for k in neighbours) >= 1

    return problem, {"nodes": nodes}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
