# clock_triplets: a Paramita (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/clock_triplets.html
# Install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python clock_triplets.py

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf


def create_model(instance):
    """Place the numbers 1 to 12 on the face of a clock so that no three adjacent
    numbers, counting round from 12 back to 1, add up to more than 21."""
    n_numbers = 12  # the numbers 1 to 12, one for each clock position
    max_sum = 21    # the largest allowed sum of three adjacent numbers

    # at[i][v] is true when clock position i holds the number v + 1
    at = [[Bool(f"x_{i}_{v}") for v in range(n_numbers)] for i in range(n_numbers)]

    constraints = []  # the rules of the puzzle

    # Each clock position holds exactly one number.
    constraints += [sum(at[i]) == 1 for i in range(n_numbers)]

    # Each number from 1 to 12 is on exactly one clock position.
    constraints += [sum(at[i][v] for i in range(n_numbers)) == 1 for v in range(n_numbers)]

    # x[i] is the number at clock position i.
    x = [sum((v + 1) * at[i][v] for v in range(n_numbers)) for i in range(n_numbers)]

    # Every three adjacent numbers, counting round the face, add up to at most max_sum.
    constraints += [x[i] + x[(i + 1) % n_numbers] + x[(i + 2) % n_numbers] <= max_sum
                    for i in range(n_numbers)]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"x": x}


if __name__ == "__main__":
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import SatSolver

    (formula, pool), outputs = create_model({})

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
