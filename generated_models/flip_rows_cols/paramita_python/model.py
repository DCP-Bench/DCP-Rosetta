# flip_rows_cols: a Paramita (Python) model from DCP Rosetta.
# Download the `flip_rows_cols.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/flip_rows_cols.html
# Then install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python flip_rows_cols.py flip_rows_cols.json

from paramita.containers import WcnfFormula
from paramita.modelling import (
    And, Bool, DimacsVariablePool, Iff, add_to_weighted_container, to_cnf,
)


def create_model(instance):
    """Flip the sign of whole rows and whole columns of a matrix of positive and negative
    numbers, so that every row and every column sums to a positive number or zero, with
    the smallest possible total of all numbers."""
    matrix = instance["input_matrix"]  # matrix[i][j]: the number in row i, column j
    n_rows = len(matrix)               # the number of rows
    n_cols = len(matrix[0])            # the number of columns

    # flip_row[i] is true when row i is flipped
    flip_row = [Bool(f"flip_row_{i}") for i in range(n_rows)]
    # flip_col[j] is true when column j is flipped
    flip_col = [Bool(f"flip_col_{j}") for j in range(n_cols)]
    # flip_cell[i][j] is true when the number in row i, column j changes sign
    flip_cell = [[Bool(f"flip_cell_{i}_{j}") for j in range(n_cols)] for i in range(n_rows)]

    # The number in row i, column j after the flips: its size stays, and it changes sign when its cell is flipped.
    def signed(i, j):
        return matrix[i][j] - 2 * matrix[i][j] * flip_cell[i][j]

    constraints = []

    # A cell is flipped exactly when one of its row and its column is flipped, not both.
    for i in range(n_rows):
        for j in range(n_cols):
            constraints.append(Iff(flip_cell[i][j], flip_row[i] + flip_col[j] == 1))

    # Flipping every row and every column together changes no sign, so the first row is never flipped.
    constraints.append(~flip_row[0])

    # Every row sums to zero or more after the flips.
    for i in range(n_rows):
        constraints.append(sum(signed(i, j) for j in range(n_cols)) >= 0)

    # Every column sums to zero or more after the flips.
    for j in range(n_cols):
        constraints.append(sum(signed(i, j) for i in range(n_rows)) >= 0)

    # The total of all numbers after the flips, to be as small as possible.
    total = sum(signed(i, j) for i in range(n_rows) for j in range(n_cols))

    # The sign of each row and of each column: -1 when flipped, 1 otherwise.
    row_signs = [1 - 2 * flip_row[i] for i in range(n_rows)]
    col_signs = [1 - 2 * flip_col[j] for j in range(n_cols)]

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # minimise as soft clauses, negated because MaxSAT maximises. The pool gives
    # each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(-total, And(constraints), to_cnf, formula, pool)

    return (formula, pool), {"row_signs": row_signs, "col_signs": col_signs}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import MAXSAT_ANSWER, MaxSatSolver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    (formula, pool), outputs = create_model(instances[index])

    solver = MaxSatSolver.from_name("EvalMaxSAT2022")
    # copy the formula into the solver: the hard clauses, then each soft clause with its weight
    solver.add_clauses(formula.hard_clauses())
    for weight, clause in formula.soft_clauses():
        solver.add_clause(clause, weight)

    if solver.solve() == MAXSAT_ANSWER.OPTIMAL:
        # the value of every variable by name: a literal is true when it is positive
        truth = {pool.decode_literal(abs(lit)).name: lit > 0 for lit in solver.model()}
        value = np.vectorize(lambda e: evaluate(e, truth))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
