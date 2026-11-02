# futoshiki: a Paramita (Python) model from DCP Rosetta.
# Download the `futoshiki.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/futoshiki.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python futoshiki.py futoshiki.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf


def create_model(instance):
    """Futoshiki: fill an n_rows-by-n_rows grid with the digits 1 to n_rows so that every row
    and every column holds each digit once, the given digits are in place, and every
    inequality sign holds."""
    values = instance["values"]  # values[r][c]: the digit given in row r, column c; 0 when the cell is empty
    lt = instance["lt"]  # lt[i] = [r1, c1, r2, c2]: cell (r1, c1) is less than cell (r2, c2); rows and columns count from 1
    n_rows = len(values)  # the grid has n_rows rows and n_rows columns
    rows = range(n_rows)
    digits = range(1, n_rows + 1)

    # digit_at[r][c][k] is true when the cell in row r, column c holds digit k.
    digit_at = [[{k: Bool(f"v_{r}_{c}_{k}") for k in digits} for c in rows] for r in rows]

    # grid[r][c] is the digit in row r, column c.
    grid = [[sum(k * digit_at[r][c][k] for k in digits) for c in rows] for r in rows]

    # Each cell holds exactly one digit.
    subject_to = [sum(digit_at[r][c].values()) == 1 for r in rows for c in rows]

    # Each row contains each digit once.
    subject_to += [sum(digit_at[r][c][k] for c in rows) == 1 for r in rows for k in digits]

    # Each column contains each digit once.
    subject_to += [sum(digit_at[r][c][k] for r in rows) == 1 for c in rows for k in digits]

    # The digits given at the start stay in their cells.
    for r in rows:
        for c in rows:
            if values[r][c] > 0:
                subject_to.append(digit_at[r][c][values[r][c]])

    # Each inequality sign holds.
    for r1, c1, r2, c2 in lt:
        subject_to.append(grid[r1 - 1][c1 - 1] + 1 <= grid[r2 - 1][c2 - 1])

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in subject_to:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"grid": grid}


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
