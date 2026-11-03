# session2_maximal_independent_sets: a PySAT (Python) model from DCP Rosetta.
# Download the `session2_maximal_independent_sets.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_maximal_independent_sets.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python session2_maximal_independent_sets.py session2_maximal_independent_sets.json

from pysat.formula import CNF, IDPool


def create_model(instance):
    """Find a maximal independent set of a graph: a set of nodes, no two of them
    adjacent, to which no other node could be added."""
    n = instance["n"]                        # the number of nodes
    adjacency = instance["adjacency_list"]   # adjacency[i]: the nodes next to node i+1

    pool = IDPool()  # hands out the variable numbers

    # nodes[i] is true when node i+1 is in the set.
    nodes = [pool.id(("node", i)) for i in range(n)]

    cnf = CNF()
    for i, neighbours in enumerate(adjacency):
        # Two adjacent nodes are not both in the set.
        for neighbour in neighbours:
            j = neighbour - 1
            if i < j:
                cnf.append([-nodes[i], -nodes[j]])
        # Node i+1 is in the set or next to a node in it, so no node can be added.
        cnf.append([nodes[i]] + [nodes[k - 1] for k in neighbours])

    return cnf, {"nodes": nodes}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.solvers import Solver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        # a literal is true when it is in the model
        value = np.vectorize(lambda lit: lit in model)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
