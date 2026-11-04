# discrete_tomography: a Paramita (Python) model from DCP Rosetta.
# Download the `discrete_tomography.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/discrete_tomography.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python discrete_tomography.py discrete_tomography.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf


def create_model(instance):
    """A matrix of zeroes and ones is x-rayed from above and from the side, giving
    the number of ones in each row and in each column. Find a matrix that fits."""
    row_sums = instance["row_sums"]  # row_sums[i]: the number of ones in row i
    col_sums = instance["col_sums"]  # col_sums[j]: the number of ones in column j
    rows, cols = len(row_sums), len(col_sums)

    # x[i][j] is true when the cell in row i, column j holds a one
    x = [[Bool(f"x_{i}_{j}") for j in range(cols)] for i in range(rows)]

    cons = []

    # Each row holds as many ones as its x-ray shows.
    for i in range(rows):
        cons.append(sum(x[i]) == row_sums[i])

    # Each column holds as many ones as its x-ray shows.
    for j in range(cols):
        cons.append(sum(x[i][j] for i in range(rows)) == col_sums[j])

    # The cells of the matrix: 1 where x is true, 0 where it is false.
    matrix = [[1 * x[i][j] for j in range(cols)] for i in range(rows)]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in cons:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"matrix": matrix}


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
