# csplib_053_graceful_graphs: a PySAT (Python) model from DCP Rosetta.
# Download the `csplib_053_graceful_graphs.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_053_graceful_graphs.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python csplib_053_graceful_graphs.py csplib_053_graceful_graphs.json

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Label the nodes of a graph with m edges with distinct numbers from 0..m, so
    that the edge labels |f(x) - f(y)| are all different."""
    n_edges = instance["m"]         # the number of edges
    n_nodes = instance["n"]         # the number of nodes
    graph = instance["graph"]       # the two end nodes of each edge

    pool = IDPool()

    # The label of each node, from 0 to the number of edges.
    nodes = [Integer(f"node_{v}", 0, n_edges, vpool=pool) for v in range(n_nodes)]
    # The label of each edge, which is the gap between the labels of its two ends: from 1 to m.
    edges = [Integer(f"edge_{e}", 1, n_edges, vpool=pool) for e in range(n_edges)]
    engine = IntegerEngine(vars=nodes + edges, vpool=pool)

    # The node labels are all different.
    engine.add_alldifferent(nodes)
    # The edge labels are all different.
    engine.add_alldifferent(edges)
    cnf = engine.clausify()

    # If the two ends of an edge have labels a and b, the label of the edge is |a - b|.
    for e, (u, v) in enumerate(graph):
        for a in range(n_edges + 1):
            for b in range(n_edges + 1):
                if a != b:
                    cnf.append([-nodes[u].equals(a), -nodes[v].equals(b), edges[e].equals(abs(a - b))])

    return cnf, {"nodes": nodes, "edges": edges}


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
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
