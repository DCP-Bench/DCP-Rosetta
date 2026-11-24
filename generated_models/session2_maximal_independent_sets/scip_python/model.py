# session2_maximal_independent_sets: a SCIP (Python) model from DCP Rosetta.
# Download the `session2_maximal_independent_sets.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_maximal_independent_sets.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python session2_maximal_independent_sets.py session2_maximal_independent_sets.json

from pyscipopt import Model, quicksum


def create_model(instance):
    """Find a maximal independent set of an undirected graph: a set of nodes no two
    of which are adjacent, to which no further node can be added.

    The graph is given by the instance's node count n and its adjacency list. The
    output nodes has one variable per node, in the order of the data; it is 1 for
    the nodes in the set and 0 for the others."""
    n = instance["n"]  # the number of nodes in the graph
    # adjacency_list[i] holds the nodes adjacent to node i + 1 (the data numbers nodes from 1)
    # neighbours[i] is the same list shifted to 0-based node numbers
    neighbours = [[j - 1 for j in row] for row in instance["adjacency_list"]]

    model = Model("maximal_independent_set")

    # nodes[i] is 1 when node i + 1 is in the set, and 0 when it is not (a yes/no choice)
    nodes = [model.addVar(f"node_{i}", vtype="B") for i in range(n)]

    # An undirected edge appears in the lists of both of its ends; keep one
    # (smaller, larger) pair per edge so each edge gives one constraint
    edges = {(min(i, j), max(i, j)) for i, row in enumerate(neighbours) for j in row}

    # Independent: the two ends of an edge are not both in the set
    for i, j in sorted(edges):
        model.addCons(nodes[i] + nodes[j] <= 1)

    # Maximal: a node that is not in the set has a neighbour in it, so no node
    # can be added. A node in the set satisfies its own constraint.
    for i in range(n):
        model.addCons(nodes[i] + quicksum(nodes[j] for j in neighbours[i]) >= 1)

    # The problem has no objective: any maximal independent set is an answer.

    return model, {"nodes": nodes}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
