# sudoku: a Paramita (Python) model from DCP Rosetta.
# Download the `sudoku.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/sudoku.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python sudoku.py sudoku.json

from math import isqrt

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, If, add_to_container, to_cnf


def create_model(instance):
    """Complete a partly filled Sudoku grid so that each row, column and section holds
    every digit from 1 to n exactly once, keeping the given digits."""
    clues = instance["input_grid"]  # clues[r][c]: the digit given in row r, column c, or 0 when the cell is empty
    n_side = len(clues)             # the grid is n_side cells wide and high
    box_side = isqrt(n_side)        # a section is box_side cells wide and high
    digits = range(1, n_side + 1)   # the digits to place

    # holds[r][c][v] is true when cell (r, c) holds digit v
    holds = [[{v: Bool(f"holds_{r}_{c}_{v}") for v in digits} for c in range(n_side)] for r in range(n_side)]

    cons = []

    # Each cell holds exactly one digit.
    for r in range(n_side):
        for c in range(n_side):
            cons.append(sum(holds[r][c].values()) == 1)

    # Each row contains each digit exactly once.
    for r in range(n_side):
        for v in digits:
            cons.append(sum(holds[r][c][v] for c in range(n_side)) == 1)

    # Each column contains each digit exactly once.
    for c in range(n_side):
        for v in digits:
            cons.append(sum(holds[r][c][v] for r in range(n_side)) == 1)

    # Each section contains each digit exactly once.
    for br in range(0, n_side, box_side):
        for bc in range(0, n_side, box_side):
            for v in digits:
                cons.append(sum(holds[br + i][bc + j][v] for i in range(box_side) for j in range(box_side)) == 1)

    # The given digits stay in their cells.
    for r in range(n_side):
        for c in range(n_side):
            v = clues[r][c]
            if v != 0:
                cons.append(holds[r][c][v])

    # the digit in each cell of the solved grid
    grid = [[sum(v * holds[r][c][v] for v in digits) for c in range(n_side)] for r in range(n_side)]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in cons:
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
