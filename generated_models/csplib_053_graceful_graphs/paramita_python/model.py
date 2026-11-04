# csplib_053_graceful_graphs: a Paramita (Python) model from DCP Rosetta.
# Download the `csplib_053_graceful_graphs.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_053_graceful_graphs.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python csplib_053_graceful_graphs.py csplib_053_graceful_graphs.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, If, add_to_container, to_cnf


def create_model(instance):
    """Label the nodes of a graph with distinct numbers from 0 to m, where m is the
    number of edges, so that each edge gets the difference of the numbers on its two
    nodes and all edge labels are different."""
    n = instance["n"]          # the number of nodes
    m = instance["m"]          # the number of edges
    graph = instance["graph"]  # graph[e]: the two nodes that edge e joins
    labels = range(m + 1)      # the node labels, from 0 to m

    # node_label[v][l] is true when node v gets the label l
    node_label = [[Bool(f"node_{v}_{l}") for l in labels] for v in range(n)]
    # edge_label[e][k] is true when edge e gets the label k, for k from 1 to m
    edge_label = [{k: Bool(f"edge_{e}_{k}") for k in range(1, m + 1)} for e in range(m)]

    constraints = []

    # Each node gets exactly one label.
    constraints += [sum(node_label[v]) == 1 for v in range(n)]

    # Different nodes get different labels: each label goes to at most one node.
    constraints += [sum(node_label[v][l] for v in range(n)) <= 1 for l in labels]

    # Each edge gets exactly one label.
    constraints += [sum(edge_label[e].values()) == 1 for e in range(m)]

    # An edge gets the difference of the labels of its two nodes. The two labels
    # differ, so the difference is at least 1.
    for e, (x, y) in enumerate(graph):
        for lx in labels:
            for ly in labels:
                if lx != ly:
                    constraints.append(
                        If(node_label[x][lx] & node_label[y][ly], edge_label[e][abs(lx - ly)])
                    )

    # The edge labels are all different: each label from 1 to m is used by exactly one edge.
    constraints += [sum(edge_label[e][k] for e in range(m)) == 1 for k in range(1, m + 1)]

    # The label of each node, and the label of each edge.
    nodes = [sum(l * node_label[v][l] for l in labels) for v in range(n)]
    edges = [sum(k * edge_label[e][k] for k in range(1, m + 1)) for e in range(m)]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"nodes": nodes, "edges": edges}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import SatSolver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    (formula, pool), outputs = create_model(instances[index])

    solver = SatSolver.from_name("Cadical300")
    # copy the formula into the solver
    solver.add_clauses(formula.clauses())

    if solver.solve():
        # the value of every variable by name: a literal is true when it is positive
        truth = {pool.decode_literal(abs(lit)).name: lit > 0 for lit in solver.model()}
        value = np.vectorize(lambda e: evaluate(e, truth))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
