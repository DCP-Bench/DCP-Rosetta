# minesweeper: a PySAT (Python) model from DCP Rosetta.
# Download the `minesweeper.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/minesweeper.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python minesweeper.py minesweeper.json

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool


def create_model(instance):
    """From the numbers on the opened cells of a Minesweeper board, decide which of the unopened
    cells hold a mine. An opened cell shows how many of its neighbouring cells are mines."""
    unopened = instance["X"]              # the value that marks a cell that is not opened yet
    game = instance["game_data"]          # game[r][c]: the number on cell (r, c), or the unopened marker
    n_rows, n_cols = len(game), len(game[0])  # the number of rows and columns of the board

    pool = IDPool()

    # mines[r][c] is true when cell (r, c) holds a mine
    mines = [[pool.id(("mine", r, c)) for c in range(n_cols)] for r in range(n_rows)]

    cnf = CNF()
    for r in range(n_rows):
        for c in range(n_cols):
            if game[r][c] != unopened:
                # An opened cell is not a mine.
                cnf.append([-mines[r][c]])
                # the cells around (r, c), fewer on the edge of the board
                around = [mines[a][b]
                          for a in range(max(0, r - 1), min(n_rows, r + 2))
                          for b in range(max(0, c - 1), min(n_cols, c + 2))
                          if (a, b) != (r, c)]
                # Exactly as many of those cells are mines as the number on (r, c) shows.
                cnf.extend(CardEnc.equals(lits=around, bound=game[r][c], vpool=pool,
                                          encoding=EncType.seqcounter).clauses)

    return cnf, {"mines": mines}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.solvers import Solver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        # a literal is true when it is in the model
        value = np.vectorize(lambda lit: lit in model)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
