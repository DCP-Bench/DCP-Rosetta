# isbn: a Paramita (Python) model from DCP Rosetta.
# Download the `isbn.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/isbn.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python isbn.py isbn.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf


def create_model(instance):
    """Fill in the unknown digits of a 13-digit ISBN so that it is valid: it starts with
    978 or 979, and its last digit is the check digit of the first 12 digits, which are
    weighted alternately by 1 and 3."""
    given = instance["isbn_init"]  # the digits of the ISBN, -1 for an unknown digit
    n_digits = len(given)

    # digit[i][v] is true when digit i of the ISBN is v
    digit = [{v: Bool(f"digit_{i}_{v}") for v in range(10)} for i in range(n_digits)]

    # Each position of the ISBN holds exactly one digit from 0 to 9.
    constraints = [sum(digit[i].values()) == 1 for i in range(n_digits)]

    # The known digits keep their value.
    for i, g in enumerate(given):
        if g >= 0:
            constraints.append(digit[i][g] == 1)

    # value[i] is digit i of the ISBN as a number
    value = [sum(v * digit[i][v] for v in range(10)) for i in range(n_digits)]

    # An ISBN-13 starts with 978 or 979.
    constraints.append(digit[0][9] == 1)
    constraints.append(digit[1][7] == 1)
    constraints.append(digit[2][8] + digit[2][9] == 1)

    # weighted is the sum of the first 12 digits, weighted alternately by 1 and 3.
    weights = [1 if i % 2 == 0 else 3 for i in range(n_digits - 1)]
    weighted = sum(w * value[i] for i, w in enumerate(weights))

    # The check digit is 0 to 9, so the weighted sum plus the check digit is a multiple
    # of 10. multiple[q] is true when that total is 10 * q.
    max_sum = sum(9 * w for w in weights) + 9
    multiple = {q: Bool(f"multiple_{q}") for q in range(1, max_sum // 10 + 1)}

    # Exactly one such multiple of 10 is taken.
    constraints.append(sum(multiple.values()) == 1)

    # The weighted sum plus the check digit is that multiple of 10.
    constraints.append(weighted + value[n_digits - 1] == sum(10 * q * multiple[q] for q in multiple))

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"isbn": value}


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
