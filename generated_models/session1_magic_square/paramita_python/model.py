# session1_magic_square: a Paramita (Python) model from DCP Rosetta.
# Download the `session1_magic_square.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_magic_square.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python session1_magic_square.py session1_magic_square.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf


def create_model(instance):
    """Fill an n x n grid with the numbers 1 to n^2, each used once, so that every
    row, every column and both diagonals add up to the same sum."""
    n = instance["n"]  # the number of rows and columns of the square

    # The common sum is n * (n^2 + 1) / 2: the numbers 1..n^2 total
    # n^2 * (n^2 + 1) / 2, shared equally between n rows.
    magic_sum = n * (n * n + 1) // 2

    # the numbers the square is filled with
    values = range(1, n * n + 1)

    # x[i][j][v] is true when the cell in row i, column j holds the number v
    x = [[{v: Bool(f"x_{i}_{j}_{v}") for v in values} for j in range(n)] for i in range(n)]
    constraints = []

    # Each cell holds exactly one number.
    for i in range(n):
        for j in range(n):
            constraints.append(sum(x[i][j].values()) == 1)

    # Each number from 1 to n^2 is in exactly one cell.
    for v in values:
        constraints.append(sum(x[i][j][v] for i in range(n) for j in range(n)) == 1)

    # square[i][j] is the number in row i, column j.
    square = [[sum(v * x[i][j][v] for v in values) for j in range(n)] for i in range(n)]

    # Every row adds up to the magic sum.
    for i in range(n):
        constraints.append(sum(square[i]) == magic_sum)

    # Every column adds up to the magic sum.
    for j in range(n):
        constraints.append(sum(square[i][j] for i in range(n)) == magic_sum)

    # The main diagonal adds up to the magic sum.
    constraints.append(sum(square[i][i] for i in range(n)) == magic_sum)

    # The other diagonal adds up to the magic sum.
    constraints.append(sum(square[i][n - 1 - i] for i in range(n)) == magic_sum)

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"square": square}


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
