# session2_maximal_independent_sets: a PyCSP3 model from DCP Rosetta.
# Download the `session2_maximal_independent_sets.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_maximal_independent_sets.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python session2_maximal_independent_sets.py session2_maximal_independent_sets.json

from pycsp3 import *


def create_model(instance):
    """In graph theory, an independent set is a set of vertices in a graph, no two of which are adjacent. A maximal
    independent set is an independent set that is not a subset of any other independent set. Find a maximal independent
    set for the data provided. The data provides an array containing for each node of the graph the set of adjacent
    nodes."""
    n_nodes = instance["n"]                    # the number of nodes of the graph, numbered from 1 in the data
    adjacency = instance["adjacency_list"]     # adjacency[i] lists the nodes adjacent to node i + 1, numbered from 1

    # nodes[i] is 1 when node i + 1 is in the independent set, 0 otherwise.
    nodes = VarArray(size=n_nodes, dom={0, 1})

    satisfy(
        # No two adjacent nodes are both in the set.
        [nodes[i] + nodes[j - 1] <= 1 for i, neighbours in enumerate(adjacency) for j in neighbours],
        # Each node is in the set or has a neighbour in it, so no node can be added to the set. Given the first
        # constraint, this is what makes the independent set maximal.
        [nodes[i] + Sum(nodes[j - 1] for j in neighbours) >= 1 for i, neighbours in enumerate(adjacency)],
    )

    return {"nodes": nodes}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())
