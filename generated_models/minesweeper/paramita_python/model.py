# minesweeper: a Paramita (Python) model from DCP Rosetta.
# Download the `minesweeper.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/minesweeper.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python minesweeper.py minesweeper.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf


def create_model(instance):
    """From the numbers on the opened cells of a Minesweeper board, decide which unopened
    ('X') cells hold a mine. An opened cell shows how many of its neighbouring cells, up to
    eight, hold a mine."""
    unopened = instance["X"]       # the marker of a cell that is not opened yet
    board = instance["game_data"]  # board[r][c]: the number on cell (r, c), or the unopened marker
    rows, cols = len(board), len(board[0])  # board height and width

    # mines[r][c] is true when cell (r, c) holds a mine
    mine = [[Bool(f"mine_{r}_{c}") for c in range(cols)] for r in range(rows)]

    # An opened cell holds no mine.
    constraints = []
    for r in range(rows):
        for c in range(cols):
            if board[r][c] != unopened:
                constraints.append(~mine[r][c])

    # The number on an opened cell is the count of mines among the cells around it.
    for r in range(rows):
        for c in range(cols):
            if board[r][c] == unopened:
                continue
            # the cells around (r, c) that lie on the board
            neighbours = [
                mine[rr][cc]
                for rr in range(r - 1, r + 2)
                for cc in range(c - 1, c + 2)
                if (rr, cc) != (r, c) and 0 <= rr < rows and 0 <= cc < cols
            ]
            constraints.append(sum(neighbours) == board[r][c])

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"mines": [[mine[r][c] for c in range(cols)] for r in range(rows)]}


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
