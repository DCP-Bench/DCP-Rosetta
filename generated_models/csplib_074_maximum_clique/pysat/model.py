# csplib_074_maximum_clique: a PySAT (Python) model from DCP Rosetta.
# Download the `csplib_074_maximum_clique.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_074_maximum_clique.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python csplib_074_maximum_clique.py csplib_074_maximum_clique.json

from pysat.formula import IDPool, WCNF


def create_model(instance):
    """In a simple undirected graph, find a clique (a set of vertices that are all
    pairwise adjacent) of the largest possible size."""
    n_vertices = instance["n"]  # number of vertices
    adj = instance["adj"]       # adj[i][j] is 1 when vertices i and j are joined by an edge, else 0

    pool = IDPool()

    # c[i] is true when vertex i is in the clique
    c = [pool.id(("c", i)) for i in range(n_vertices)]

    formula = WCNF()

    # Two vertices that are not joined by an edge cannot both be in the clique.
    for i in range(n_vertices):
        for j in range(i + 1, n_vertices):
            if adj[i][j] == 0:
                formula.append([-c[i], -c[j]])

    # Each vertex left out of the clique costs 1, so the cheapest choice is the largest clique.
    for i in range(n_vertices):
        formula.append([c[i]], weight=1)

    return formula, {"c": c}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.examples.rc2 import RC2Stratified

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    # falsify as little soft-clause weight as possible
    model = RC2Stratified(formula).compute()

    if model:
        # a literal is true when it is in the model
        value = np.vectorize(lambda lit: lit in model)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
