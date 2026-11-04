# just_forgotten: a Paramita (Python) model from DCP Rosetta.
# Download the `just_forgotten.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/just_forgotten.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python just_forgotten.py just_forgotten.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf


def create_model(instance):
    """Joe forgot his bank account number. It has all the digits from 0 to n-1 in some
    order. In each set of digits he tried, a given number of the digits were in their
    correct position. Find the account number."""
    sets = instance["sets"]  # sets[s][i]: the digit at position i of the s-th set Joe tried
    num_correct = instance["num_correct_digits"]  # digits in the right position in each set
    n_digits = len(sets[0])  # the number of digits in the account number

    # digit_at[i][v] is true when the account number has digit v at position i
    digit_at = [[Bool(f"digit_at_{i}_{v}") for v in range(n_digits)] for i in range(n_digits)]

    # Each position of the account number holds exactly one digit.
    constraints = [sum(digit_at[i]) == 1 for i in range(n_digits)]

    # Each digit from 0 to n-1 is at exactly one position.
    constraints += [sum(digit_at[i][v] for i in range(n_digits)) == 1 for v in range(n_digits)]

    # In each set Joe tried, exactly num_correct digits are in the right position.
    for s in sets:
        constraints.append(sum(digit_at[i][s[i]] for i in range(n_digits)) == num_correct)

    # x[i] is the digit at position i of the account number.
    x = [sum(v * digit_at[i][v] for v in range(n_digits)) for i in range(n_digits)]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"x": x}


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
