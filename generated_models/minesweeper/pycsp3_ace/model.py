# minesweeper: a PyCSP3 model from DCP Rosetta.
# Download the `minesweeper.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/minesweeper.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python minesweeper.py minesweeper.json

from pycsp3 import *


def create_model(instance):
    """Minesweeper: the board is divided into cells, with mines distributed among them. The number
    on a cell shows the number of mines adjacent to it. Determine which unopened cells contain mines
    from the numerical clues on the opened cells."""
    unopened = instance["X"]           # the value that marks an unopened cell
    game_data = instance["game_data"]  # game_data[i][j]: the clue on cell (i, j), or unopened
    n_rows = len(game_data)
    n_cols = len(game_data[0])

    # mines[i][j] is 1 when cell (i, j) holds a mine, 0 otherwise.
    mines = VarArray(size=[n_rows, n_cols], dom={0, 1})

    # The cells next to cell (i, j), diagonals included, that lie on the board.
    def adjacent(i, j):
        return [
            (a, b)
            for a in range(max(i - 1, 0), min(i + 2, n_rows))
            for b in range(max(j - 1, 0), min(j + 2, n_cols))
            if (a, b) != (i, j)
        ]

    # The opened cells, those that show a clue.
    opened = [(i, j) for i in range(n_rows) for j in range(n_cols) if game_data[i][j] != unopened]

    satisfy(
        # An opened cell holds no mine: a mine cannot be opened (taken as the rule of the game).
        [mines[i][j] == 0 for i, j in opened],
        # The clue on an opened cell is the number of mines among the cells next to it.
        [Sum(mines[a][b] for a, b in adjacent(i, j)) == game_data[i][j] for i, j in opened],
    )

    return {"mines": mines}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        print("mines", "=")
        for row in outputs["mines"]:
            print(values(row))
    else:
        print("No solution:", status())
