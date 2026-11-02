# session2_subsets_100: a Paramita (Python) model from DCP Rosetta.
# Download the `session2_subsets_100.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_subsets_100.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python session2_subsets_100.py session2_subsets_100.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf


def create_model(instance):
    """Given a set A of different integers, find two disjoint non-empty subsets
    S and T of A such that the elements of S sum to the same value as the
    elements of T."""
    A = instance["A"]          # A[i]: the i-th integer of the set
    n_integers = len(A)        # the number of integers in the set

    # in_S[i] is true when the i-th integer belongs to S
    in_S = [Bool(f"in_S_{i}") for i in range(n_integers)]
    # in_T[i] is true when the i-th integer belongs to T
    in_T = [Bool(f"in_T_{i}") for i in range(n_integers)]

    # S and T are disjoint: no integer lies in both.
    subject_to = [~(in_S[i] & in_T[i]) for i in range(n_integers)]

    # S is non-empty.
    subject_to.append(sum(in_S) >= 1)

    # T is non-empty.
    subject_to.append(sum(in_T) >= 1)

    # S and T have the same sum.
    subject_to.append(sum(A[i] * in_S[i] for i in range(n_integers))
                      == sum(A[i] * in_T[i] for i in range(n_integers)))

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in subject_to:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"in_S": in_S, "in_T": in_T}


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
