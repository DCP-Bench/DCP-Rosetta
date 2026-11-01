# minesweeper: a CPMpy model from DCP Rosetta.
# Download the `minesweeper.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/minesweeper.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python minesweeper.py minesweeper.json

import cpmpy as cp


def create_model(instance):
    """From the numbers on the opened cells of a Minesweeper board, decide which
    unopened ('X') cells hold a mine. An opened cell shows how many of its
    neighbouring cells are mines."""
    unopened = instance["X"]       # the value that marks a cell that is not opened yet
    game = instance["game_data"]   # game[r][c]: the number of mines around cell (r, c), or the unopened marker
    rows, cols = len(game), len(game[0])

    # mines[r, c] is true when cell (r, c) holds a mine
    mines = cp.boolvar(shape=(rows, cols), name="mines")

    model = cp.Model()
    for r in range(rows):
        for c in range(cols):
            if game[r][c] == unopened:
                continue

            # An opened cell is not a mine.
            model.add(~mines[r, c])

            # The number on an opened cell is the number of mines among its neighbours:
            # the cells around it, fewer at the border of the board.
            neighbours = mines[max(r - 1, 0):r + 2, max(c - 1, 0):c + 2]
            model.add(cp.sum(neighbours) == game[r][c])  # the cell itself is no mine, so it adds 0

    return model, {"mines": mines}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
