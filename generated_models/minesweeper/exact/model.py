# minesweeper: an Exact (Python) model from DCP Rosetta.
# Download the `minesweeper.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/minesweeper.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python minesweeper.py minesweeper.json

from exact import Exact


def create_model(instance):
    """From the numbers on the opened cells of a Minesweeper board, decide which
    unopened ('X') cells hold a mine. An opened cell shows how many of its
    neighbouring cells are mines."""
    unopened = instance["X"]      # the value that marks a cell that is not opened yet
    game = instance["game_data"]  # game[r][c]: the number on cell (r, c), or the unopened marker
    n_rows = len(game)     # the number of rows of the board
    n_cols = len(game[0])  # the number of columns of the board

    solver = Exact()

    # Exact identifies its variables by name.
    # mines[r][c] is 1 when cell (r, c) holds a mine, and 0 when not.
    # An opened cell is safe, so only unopened cells can hold a mine.
    mines = [[f"mine_{r}_{c}" for c in range(n_cols)] for r in range(n_rows)]
    for r in range(n_rows):
        for c in range(n_cols):
            solver.addVariable(mines[r][c], 0, 1 if game[r][c] == unopened else 0)

    # The number on each opened cell is the count of mines among its neighbouring cells.
    for r in range(n_rows):
        for c in range(n_cols):
            if game[r][c] != unopened:
                around = [(1, mines[a][b])
                          for a in range(max(0, r - 1), min(n_rows, r + 2))
                          for b in range(max(0, c - 1), min(n_cols, c + 2))
                          if (a, b) != (r, c)]
                solver.addConstraint(around, True, game[r][c], True, game[r][c])

    return solver, {"mines": mines}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
