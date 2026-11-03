# added_corners: a Paramita (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/added_corners.html
# Install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python added_corners.py

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf


def create_model(instance):
    """Enter the digits 1 through 8 in the circles and squares of a figure so that
    the number in each square is the sum of the numbers in the adjoining circles.
    Give the digit at each position, reading left to right and top to bottom."""
    n_cells = 8  # the circles and squares of the figure
    digits = range(1, n_cells + 1)  # the digits to enter

    # x[p][v] is true when cell p holds digit v. Cells are numbered 0 to 7 in reading
    # order, skipping the empty middle.
    x = [{v: Bool(f"x_{p}_{v}") for v in digits} for p in range(n_cells)]
    # The digit in cell p.
    digit = [sum(v * x[p][v] for v in digits) for p in range(n_cells)]

    # Each cell holds exactly one digit.
    constraints = [sum(x[p].values()) == 1 for p in range(n_cells)]
    # Each digit is in exactly one cell.
    constraints += [sum(x[p][v] for p in range(n_cells)) == 1 for v in digits]
    # Each square holds the sum of the two circles next to it.
    constraints += [
        digit[1] == digit[0] + digit[2],  # top square, between circles 0 and 2
        digit[3] == digit[0] + digit[5],  # left square, between circles 0 and 5
        digit[4] == digit[2] + digit[7],  # right square, between circles 2 and 7
        digit[6] == digit[5] + digit[7],  # bottom square, between circles 5 and 7
    ]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"positions": digit}


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
