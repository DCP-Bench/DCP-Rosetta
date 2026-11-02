# kakuro: a Paramita (Python) model from DCP Rosetta.
# Download the `kakuro.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/kakuro.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python kakuro.py kakuro.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf


def create_model(instance):
    """Fill the white cells of a Kakuro grid with digits 1 to 9 so that the digits of
    each entry add up to its clue and no digit is repeated within an entry."""
    n = instance["n"]              # the grid is n by n
    blanks = instance["blanks"]    # the black cells, as [row, col] (1-based)
    entries = instance["problem"]  # each entry: its clue, then the cells it covers, as [row, col] (1-based)

    black = {tuple(cell) for cell in blanks}  # the black cells
    white = [(r, c) for r in range(1, n + 1) for c in range(1, n + 1) if (r, c) not in black]  # the cells that take a digit
    digits = range(1, 10)  # the digits 1 to 9

    # holds[cell][v] is true when the white cell holds digit v
    holds = {cell: {v: Bool(f"x_{cell[0]}_{cell[1]}_{v}") for v in digits} for cell in white}

    cons = []  # the rules of the puzzle

    # Each white cell holds exactly one digit.
    for cell in white:
        cons.append(sum(holds[cell].values()) == 1)

    for clue, *cells in entries:
        cells = [tuple(cell) for cell in cells]

        # No digit appears twice in an entry.
        for v in digits:
            cons.append(sum(holds[cell][v] for cell in cells) <= 1)

        # The digits of the entry add up to its clue.
        cons.append(sum(v * holds[cell][v] for cell in cells for v in digits) == clue)

    # x[r][c] is the digit in the cell at row r, column c; 0 on black cells.
    x = []
    for r in range(1, n + 1):
        row = []
        for c in range(1, n + 1):
            if (r, c) in holds:
                row.append(sum(v * holds[(r, c)][v] for v in digits))
            else:
                row.append(0)
        x.append(row)

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in cons:
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
