# csplib_074_maximum_clique: a hermax (Python) model from DCP Rosetta.
# Download the `csplib_074_maximum_clique.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_074_maximum_clique.html
# Then run it on the first instance (after `pip install hermax`):
#   python csplib_074_maximum_clique.py csplib_074_maximum_clique.json

from hermax.model import Model


def create_model(instance):
    """Maximum clique: in a simple undirected graph, choose the largest set of vertices in
    which every two distinct vertices are adjacent. Output c[i] = 1 when vertex i is in
    the clique, 0 otherwise."""
    n = instance["n"]        # n: the number of vertices, numbered 0 .. n-1
    adj = instance["adj"]    # adj[i][j]: 1 when vertices i and j are joined by an edge, 0 otherwise

    m = Model()

    # c[i] is true when vertex i is in the clique
    c = m.bool_vector("c", n)

    # Two distinct vertices with no edge between them cannot both be in the clique.
    for i in range(n):
        for j in range(i + 1, n):
            if not adj[i][j]:
                m &= (~c[i]) | (~c[j])

    # Maximise the number of chosen vertices. Minimising the number of vertices left out
    # is the same thing, since every vertex is either in the clique or out of it.
    m.obj += sum(~c[i] for i in range(n))

    # The objective in the problem's terms: the clique size; the solver minimises the vertices
    # left out, n minus that size.
    clique_size = sum(c[i] for i in range(n))
    return m, {"c": c}, clique_size


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
        print("objective =", result[objective])
    else:
        print("No solution:", result.status)
