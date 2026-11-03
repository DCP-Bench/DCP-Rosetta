# session2_maximal_independent_sets: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `session2_maximal_independent_sets.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_maximal_independent_sets.html
# Then run it on the first instance (after `pip install ortools`):
#   python session2_maximal_independent_sets.py session2_maximal_independent_sets.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Find a maximal independent set of a graph: a set of nodes, no two of
    them adjacent, such that every node outside the set is adjacent to a node in it."""
    n_nodes = instance["n"]  # the number of nodes
    adjacency_list = instance["adjacency_list"]  # adjacency_list[i]: the nodes adjacent to node i+1

    model = cp_model.CpModel()

    # nodes[i] is true when node i+1 is in the set
    nodes = [model.new_bool_var(f"node_{i}") for i in range(n_nodes)]

    for i, neighbours in enumerate(adjacency_list):
        # Independent: no two adjacent nodes are both in the set, checked once per pair.
        for neighbour in neighbours:
            j = neighbour - 1
            if i < j:
                model.add_at_most_one([nodes[i], nodes[j]])
        # Maximal: node i+1 is in the set or has a neighbour in it, so it cannot be added.
        model.add_bool_or([nodes[i]] + [nodes[k - 1] for k in neighbours])

    return model, {"nodes": nodes}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
