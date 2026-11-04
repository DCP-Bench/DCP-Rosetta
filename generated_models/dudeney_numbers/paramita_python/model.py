# dudeney_numbers: a Paramita (Python) model from DCP Rosetta.
# Download the `dudeney_numbers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/dudeney_numbers.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python dudeney_numbers.py dudeney_numbers.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf


def create_model(instance):
    """A Dudeney number is a positive integer that is a perfect cube such that the
    sum of its digits is equal to the cube root of the number. Find such a number
    that is larger than 1."""
    n = instance["n"]  # the most digits the number can have

    # is_digit[p][v] is true when digit place p holds the digit v. Place 0 is the units place.
    is_digit = [[Bool(f"digit_{p}_is_{v}") for v in range(10)] for p in range(n)]
    constraints = []

    # Each digit place holds exactly one digit.
    constraints += [sum(is_digit[p]) == 1 for p in range(n)]

    # digit[p] is the digit in place p
    digit = [sum(v * is_digit[p][v] for v in range(10)) for p in range(n)]

    # The digits add up to at most 9 * n, so the cube root is at most 9 * n.
    max_root = 9 * n
    # is_root[r] is true when the cube root of the number is r. A number larger than 1 has a root of at least 2.
    is_root = {r: Bool(f"root_is_{r}") for r in range(2, max_root + 1)}
    # The cube root is exactly one of these values.
    constraints.append(sum(is_root.values()) == 1)

    # The number, with digit p in place p.
    number = sum(10 ** p * digit[p] for p in range(n))
    # The number is the cube of its root.
    constraints.append(number == sum(r ** 3 * is_root[r] for r in is_root))
    # The digits add up to the root.
    constraints.append(sum(digit) == sum(r * is_root[r] for r in is_root))

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"number": number}


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
