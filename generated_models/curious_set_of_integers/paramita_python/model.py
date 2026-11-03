# curious_set_of_integers: a Paramita (Python) model from DCP Rosetta.
# Download the `curious_set_of_integers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/curious_set_of_integers.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python curious_set_of_integers.py curious_set_of_integers.json

from math import isqrt

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, If, add_to_container, to_cnf

GIVEN = [1, 3, 8, 120]  # the integers already in the set


def create_model(instance):
    """The integers 1, 3, 8 and 120 form a set in which the product of any two
    integers is one less than a perfect square. Find a fifth number (at least 0)
    that can be added to the set without destroying this property."""
    max_val = instance["max_val"]  # the largest value the new number can take
    n = instance["n"]  # the size of the set with the new number added
    assert len(GIVEN) + 1 == n  # the set holds the given integers and the new one

    n_bits = max_val.bit_length()  # the binary digits needed to write max_val

    # the new number in base two, lowest place first
    bits = [Bool(f"number_bit_{k}") for k in range(n_bits)]
    number = sum((2**k) * bits[k] for k in range(n_bits))
    constraints = []  # the conditions the new number must meet

    # The new number is at most max_val.
    constraints.append(number <= max_val)

    # The product of each given integer with the new number is one less than a perfect square.
    for a in GIVEN:
        max_root = isqrt(a * max_val + 1)  # the largest root that can occur
        n_square_bits = (max_root * max_root).bit_length()  # the binary digits needed for the largest square
        # roots[c] is true when c is the chosen square root of a * number + 1
        roots = {c: Bool(f"root_{a}_{c}") for c in range(1, max_root + 1)}
        # the square of the chosen root, lowest place first
        square_bits = [Bool(f"square_{a}_{k}") for k in range(n_square_bits)]
        constraints.append(sum(roots.values()) == 1)
        for c in roots:
            square = c * c
            for k in range(n_square_bits):
                if (square >> k) & 1:
                    constraints.append(If(roots[c], square_bits[k]))
                else:
                    constraints.append(If(roots[c], ~square_bits[k]))
        # the square of the chosen root is a * number + 1
        constraints.append(sum((2**k) * square_bits[k] for k in range(n_square_bits)) == a * number + 1)

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
