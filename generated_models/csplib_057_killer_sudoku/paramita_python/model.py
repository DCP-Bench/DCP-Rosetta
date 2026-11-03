# csplib_057_killer_sudoku: a Paramita (Python) model from DCP Rosetta.
# Download the `csplib_057_killer_sudoku.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_057_killer_sudoku.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python csplib_057_killer_sudoku.py csplib_057_killer_sudoku.json

from math import isqrt

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf


def create_model(instance):
    """Fill an n by n grid with the digits 1 to n so that every row, column and box
    holds each digit once, and every cage (a group of cells) adds up to the total in
    its corner, with no digit repeated inside a cage."""
    n = instance["n"]            # the side of the grid
    cages = instance["problem"]  # each cage: [total, cells], with the cells as (row, column) pairs counted from 1
    box = isqrt(n)               # the side of a box (3 for a 9 by 9 grid)
    digits = range(1, n + 1)

    # holds[r][c][v] is true when the cell in row r, column c holds the digit v
    holds = [[{v: Bool(f"holds_{r}_{c}_{v}") for v in digits} for c in range(n)] for r in range(n)]

    constraints = []

    # Each cell holds exactly one digit.
    constraints += [sum(holds[r][c].values()) == 1 for r in range(n) for c in range(n)]

    # Each row holds each digit once.
    constraints += [sum(holds[r][c][v] for c in range(n)) == 1 for r in range(n) for v in digits]

    # Each column holds each digit once.
    constraints += [sum(holds[r][c][v] for r in range(n)) == 1 for c in range(n) for v in digits]

    # Each box holds each digit once.
    for br in range(0, n, box):
        for bc in range(0, n, box):
            cells = [(br + dr, bc + dc) for dr in range(box) for dc in range(box)]
            constraints += [sum(holds[r][c][v] for r, c in cells) == 1 for v in digits]

    for total, cage_cells in cages:
        positions = [(r - 1, c - 1) for r, c in cage_cells]

        # The digits in the cage add up to its total.
        constraints.append(sum(v * holds[r][c][v] for r, c in positions for v in digits) == total)

        # No digit repeats inside the cage.
        constraints += [sum(holds[r][c][v] for r, c in positions) <= 1 for v in digits]

    # The digit in each cell.
    grid = [[sum(v * holds[r][c][v] for v in digits) for c in range(n)] for r in range(n)]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"x": grid}


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
