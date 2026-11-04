# autoref: a Paramita (Python) model from DCP Rosetta.
# Download the `autoref.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/autoref.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python autoref.py autoref.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf


def create_model(instance):
    """Find a series s[0], ..., s[n+1] of whole numbers in which every value i from 0
    to n occurs exactly s[i] times, and whose last entry s[n+1] equals m."""
    n = instance["n"]  # the series counts the values 0 to n
    m = instance["m"]  # the required last entry of the series

    n_entries = n + 2  # the series has n + 2 entries
    largest = n        # no entry is larger than n

    # x[k][v] is true when entry k of the series has the value v
    x = [[Bool(f"x_{k}_{v}") for v in range(largest + 1)] for k in range(n_entries)]
    # s[k] is the value of entry k; value 0 adds nothing to the sum
    s = [sum(v * x[k][v] for v in range(1, largest + 1)) for k in range(n_entries)]

    constraints = []

    # Every entry has exactly one value.
    for k in range(n_entries):
        constraints.append(sum(x[k]) == 1)

    # The value i occurs s[i] times in the series, for each i from 0 to n.
    for i in range(n + 1):
        constraints.append(sum(x[k][i] for k in range(n_entries)) == s[i])

    # The last entry is m.
    constraints.append(s[n + 1] == m)

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"s": s}


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
