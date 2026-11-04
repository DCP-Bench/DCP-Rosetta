# csplib_044_steiner: a Paramita (Python) model from DCP Rosetta.
# Download the `csplib_044_steiner.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_044_steiner.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python csplib_044_steiner.py csplib_044_steiner.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf


def create_model(instance):
    """Find n * (n - 1) / 6 triples of distinct elements of {1, ..., n} such that any two
    triples have at most one element in common (n is 1 or 3 modulo 6)."""
    n = instance["n"]                # the number of elements
    n_triples = n * (n - 1) // 6     # the number of triples the system needs

    # sets[i][e] is true when element e belongs to triple i
    sets = [[Bool(f"sets_{i}_{e}") for e in range(n)] for i in range(n_triples)]

    # Each triple has three elements.
    constraints = [sum(triple) == 3 for triple in sets]

    # Any two triples have at most one element in common.
    for i in range(n_triples):
        for k in range(i + 1, n_triples):
            constraints.append(sum(sets[i][e] & sets[k][e] for e in range(n)) <= 1)

    # Every pair of elements lies in exactly one triple.
    for e in range(n):
        for f in range(e + 1, n):
            constraints.append(sum(sets[i][e] & sets[i][f] for i in range(n_triples)) == 1)

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"sets": sets}


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
