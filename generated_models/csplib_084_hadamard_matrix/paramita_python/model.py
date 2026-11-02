# csplib_084_hadamard_matrix: a Paramita (Python) model from DCP Rosetta.
# Download the `csplib_084_hadamard_matrix.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_084_hadamard_matrix.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python csplib_084_hadamard_matrix.py csplib_084_hadamard_matrix.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, Iff, add_to_container, to_cnf


def create_model(instance):
    """Find two sequences a and b of odd length l, with entries -1 or +1, that each
    sum to 1 and whose periodic autocorrelations add up to -2 at every shift
    s = 1, ..., (l-1)/2 (a Legendre pair, which gives a Hadamard matrix)."""
    l = instance["l"]                # length of each sequence, an odd number
    n_shifts = (l - 1) // 2          # the shifts s = 1, ..., n_shifts that are constrained
    plus_count = (l + 1) // 2        # a sequence of length l sums to 1 when this many entries are +1

    # a[i] is true when entry i of a is +1, and b[i] when entry i of b is +1
    a = [Bool(f"a_{i}") for i in range(l)]
    b = [Bool(f"b_{i}") for i in range(l)]

    constraints = []

    # Each sequence sums to 1.
    constraints.append(sum(a) == plus_count)
    constraints.append(sum(b) == plus_count)

    # At each shift s, the periodic autocorrelations of a and b add up to -2. Entries i and
    # i + s (indices taken modulo l) of a sequence have the same sign or not, and the two
    # autocorrelations add up to -2 exactly when a and b together have l - 1 same-sign pairs.
    for s in range(1, n_shifts + 1):
        # same_a[i] is true when entries i and i + s of a have the same sign
        same_a = [Bool(f"agree_a_{s}_{i}") for i in range(l)]
        same_b = [Bool(f"agree_b_{s}_{i}") for i in range(l)]
        for i in range(l):
            j = (i + s) % l
            constraints.append(Iff(same_a[i], Iff(a[i], a[j])))
            constraints.append(Iff(same_b[i], Iff(b[i], b[j])))
        constraints.append(sum(same_a) + sum(same_b) == l - 1)

    # The two sequences, entries -1 or +1.

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"a": [2 * x - 1 for x in a], "b": [2 * x - 1 for x in b]}


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
