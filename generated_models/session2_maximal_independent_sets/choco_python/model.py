# session2_maximal_independent_sets: a Choco-solver (Python) model from DCP Rosetta.
# Download the `session2_maximal_independent_sets.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_maximal_independent_sets.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python session2_maximal_independent_sets.py session2_maximal_independent_sets.json

from pychoco.model import Model


def create_model(instance):
    """Choose a maximal independent set of a graph: a set of nodes, no two of them adjacent, to which no further node can be added."""
    n_nodes = instance["n"]                      # number of nodes
    adjacency_list = instance["adjacency_list"]  # the nodes adjacent to each node

    model = Model()

    # nodes[i] says whether node i+1 is in the set.
    nodes = [model.boolvar(name=f"nodes_{i}") for i in range(n_nodes)]

    # Adjacent nodes are not both in the set.
    for i, neighbors in enumerate(adjacency_list):
        for neighbor in neighbors:
            j = neighbor - 1
            if i < j:
                model.sum([nodes[i], nodes[j]], "<=", 1).post()

    # Every node is in the set or next to a node in it, so no node can be added.
    for i, neighbors in enumerate(adjacency_list):
        model.sum([nodes[i]] + [nodes[neighbor - 1] for neighbor in neighbors], ">=", 1).post()

    return model, {"nodes": nodes}, None


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
