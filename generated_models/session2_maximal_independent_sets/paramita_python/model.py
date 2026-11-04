# session2_maximal_independent_sets: a Paramita (Python) model from DCP Rosetta.
# Download the `session2_maximal_independent_sets.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_maximal_independent_sets.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python session2_maximal_independent_sets.py session2_maximal_independent_sets.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, Or, add_to_container, to_cnf


def create_model(instance):
    """Find a maximal independent set of a graph: a set of nodes, no two of
    them adjacent, that cannot be extended by any further node."""
    n_nodes = instance["n"]                      # the number of nodes
    adjacency_list = instance["adjacency_list"]  # adjacency_list[i]: the nodes adjacent to node i+1, numbered from 1

    # nodes[i] is true when node i+1 is in the set
    nodes = [Bool(f"node_{i + 1}") for i in range(n_nodes)]

    subject_to = []  # the rules the set must satisfy

    # No two adjacent nodes are both in the set; each edge is listed from both ends, so it is taken once.
    for i in range(n_nodes):
        for j in adjacency_list[i]:
            if i < j - 1:
                subject_to.append(~(nodes[i] & nodes[j - 1]))

    # Every node is in the set or next to a node in it, so no node can be added.
    for i in range(n_nodes):
        subject_to.append(Or([nodes[i]] + [nodes[j - 1] for j in adjacency_list[i]]))

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in subject_to:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"nodes": nodes}


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
