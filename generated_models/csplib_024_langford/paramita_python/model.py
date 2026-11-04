# csplib_024_langford: a Paramita (Python) model from DCP Rosetta.
# Download the `csplib_024_langford.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_024_langford.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python csplib_024_langford.py csplib_024_langford.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf


def create_model(instance):
    """Arrange two copies of each number from 1 to k into one sequence of 2k places, so that
    the two 1's are one number apart, the two 2's two numbers apart, ..., and the two k's k
    numbers apart."""
    k = instance["k"]  # the largest number; each of 1 to k appears twice
    n_places = 2 * k   # the places of the sequence, all filled

    # first[i][p] is true when the first copy of number i is at place p, places numbered from 0.
    # The second copy then stands i + 1 places further on, so p stops before the end of the sequence.
    first = {i: {p: Bool(f"first_{i}_{p}") for p in range(n_places - i - 1)}
             for i in range(1, k + 1)}

    # Each number has exactly one place for its first copy.
    constraints = [sum(first[i].values()) == 1 for i in range(1, k + 1)]

    # occ[i][q] is true when a copy of number i stands at place q, as its first copy or as its second.
    occ = {i: {} for i in range(1, k + 1)}
    for i in range(1, k + 1):
        for q in range(n_places):
            occ[i][q] = sum(first[i][p] for p in (q, q - i - 1) if p in first[i])

    # Each place of the sequence holds exactly one copy.
    constraints += [sum(occ[i][q] for i in range(1, k + 1)) == 1 for q in range(n_places)]

    # sol[q] is the number at place q.
    sol = [sum(i * occ[i][q] for i in range(1, k + 1)) for q in range(n_places)]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"sol": sol}


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
