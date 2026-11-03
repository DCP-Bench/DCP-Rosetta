# minesweeper: a cvc5 (Python) model from DCP Rosetta.
# Download the `minesweeper.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/minesweeper.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python minesweeper.py minesweeper.json

import cvc5.pythonic as c5


def create_model(instance):
    """From the numbers on the opened cells of a Minesweeper board, decide which unopened
    cells hold a mine. An opened cell's number is the count of mines among its neighbours."""
    unopened = instance["X"]      # the value that marks a cell that is not opened yet
    game = instance["game_data"]  # game[r][c]: the number on cell (r, c), or the unopened marker
    n_rows = len(game)            # the number of rows on the board
    n_cols = len(game[0])         # the number of columns on the board

    # mines[r][c] is true when cell (r, c) holds a mine
    mines = [[c5.Bool(f"mine_{r}_{c}") for c in range(n_cols)] for r in range(n_rows)]

    solver = c5.Solver()

    for r in range(n_rows):
        for c in range(n_cols):
            if game[r][c] == unopened:
                continue

            # An opened cell holds no mine.
            solver.add(c5.Not(mines[r][c]))

            # The cells next to (r, c), fewer at the edge of the board.
            neighbours = [
                mines[a][b]
                for a in range(max(0, r - 1), min(n_rows, r + 2))
                for b in range(max(0, c - 1), min(n_cols, c + 2))
                if (a, b) != (r, c)
            ]

            # The number on an opened cell is the count of mines among its neighbours.
            solver.add(c5.Sum([c5.If(m, 1, 0) for m in neighbours]) == game[r][c])

    return solver, {"mines": mines}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
