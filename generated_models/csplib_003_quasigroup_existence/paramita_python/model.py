# csplib_003_quasigroup_existence: a Paramita (Python) model from DCP Rosetta.
# Download the `csplib_003_quasigroup_existence.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_003_quasigroup_existence.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python csplib_003_quasigroup_existence.py csplib_003_quasigroup_existence.json

from paramita.containers import CnfFormula
from paramita.modelling import And, Bool, DimacsVariablePool, If, add_to_container, to_cnf


def create_model(instance):
    """QG3.m quasigroup existence: find an order m quasigroup, a table of size m by m
    in which each element from 0 to m-1 occurs once in every row and every column,
    such that (a*b)*(b*a) = a for all a and b."""
    m = instance["m"]  # the order of the quasigroup: its size, and its elements run from 0 to m-1

    # product[a][b][c] is true when a*b is c.
    product = [[[Bool(f"prod_{a}_{b}_{c}") for c in range(m)] for b in range(m)]
               for a in range(m)]

    constraints = []

    # Each cell of the table holds exactly one element.
    constraints += [sum(product[a][b]) == 1 for a in range(m) for b in range(m)]
    # Each element occurs once in every row.
    constraints += [sum(product[a][b][c] for b in range(m)) == 1
                    for a in range(m) for c in range(m)]
    # Each element occurs once in every column.
    constraints += [sum(product[a][b][c] for a in range(m)) == 1
                    for b in range(m) for c in range(m)]
    # (a*b)*(b*a) = a for all a and b: with c = a*b and d = b*a, the product c*d is a.
    for a in range(m):
        for b in range(m):
            for c in range(m):
                for d in range(m):
                    constraints.append(If(And(product[a][b][c], product[b][a][d]),
                                          product[c][d][a]))

    # quasigroup[a][b]: the product a*b, an element from 0 to m-1.
    quasigroup = [[sum(c * product[a][b][c] for c in range(m)) for b in range(m)]
                  for a in range(m)]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"quasigroup": quasigroup}


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
