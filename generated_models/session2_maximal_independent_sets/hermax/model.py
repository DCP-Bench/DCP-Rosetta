# session2_maximal_independent_sets: a hermax (Python) model from DCP Rosetta.
# Download the `session2_maximal_independent_sets.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_maximal_independent_sets.html
# Then run it on the first instance (after `pip install hermax`):
#   python session2_maximal_independent_sets.py session2_maximal_independent_sets.json

from hermax.model import Model


def create_model(instance):
    """Find a maximal independent set of a graph: a set of nodes, no two of them adjacent,
    to which no other node can be added. Any such set is accepted, so there is no objective."""
    n = instance["n"]                       # n: the number of nodes, numbered 1..n in the data
    adjacency = instance["adjacency_list"]  # adjacency[i]: the neighbours of node i+1 (1-based ids)

    # The graph's edges, each once, as 0-based node pairs (a, b) with a < b.
    edges = {tuple(sorted((i, j - 1))) for i in range(n) for j in adjacency[i]}

    m = Model()

    # nodes[i] is true when node i+1 is in the independent set
    nodes = m.bool_vector("node", n)

    # Independence: the two ends of every edge are not both in the set.
    for a, b in sorted(edges):
        m &= (nodes[a] + nodes[b] <= 1)

    # Maximality: every node is in the set or has a neighbour in it,
    # so no node outside the set can be added without breaking independence.
    for i in range(n):
        neighbours = [j - 1 for j in adjacency[i]]
        m &= (nodes[i] + sum(nodes[j] for j in neighbours) >= 1)

    # No objective: any maximal independent set is a solution.

    return m, {"nodes": nodes}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
