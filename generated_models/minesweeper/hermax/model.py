# minesweeper: a hermax (Python) model from DCP Rosetta.
# Download the `minesweeper.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/minesweeper.html
# Then run it on the first instance (after `pip install hermax`):
#   python minesweeper.py minesweeper.json

from hermax.model import Model


def create_model(instance):
    """Minesweeper: from the revealed numbers on a board, decide which of the unopened
    cells hold a mine. An opened cell is safe and shows how many of its (up to eight)
    neighbours are mines. Output: mines[r][c] is true where a mine is."""
    unopened = instance["X"]        # the value that marks a cell that is not opened
    game = instance["game_data"]    # game[r][c]: the number shown on cell (r, c), or unopened
    rows, cols = len(game), len(game[0])  # board size, taken from this instance's board

    m = Model()

    # mines[r][c] is true when cell (r, c) holds a mine
    mines = m.bool_matrix("mines", rows, cols)

    for r in range(rows):
        for c in range(cols):
            if game[r][c] != unopened:
                # An opened cell is safe, so it holds no mine.
                m &= ~mines[r][c]
                # Its number is the count of mines among its neighbours.
                neighbours = [mines[a][b]
                              for a in range(max(0, r - 1), min(rows, r + 2))
                              for b in range(max(0, c - 1), min(cols, c + 2))
                              if (a, b) != (r, c)]
                m &= (sum(neighbours) == game[r][c])

    return m, {"mines": mines}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
