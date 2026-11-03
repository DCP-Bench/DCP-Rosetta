# minesweeper: a SCIP (Python) model from DCP Rosetta.
# Download the `minesweeper.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/minesweeper.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python minesweeper.py minesweeper.json

from pyscipopt import Model, quicksum
import numpy as np


def create_model(instance):
    """Minesweeper: say, for every cell of the board, whether it holds a mine.

    The board is a grid. An opened cell shows a number: how many of the cells
    around it (up to eight neighbours, the cell itself not counted) hold a mine.
    An unopened cell shows -1 and its contents are hidden. The task is to find
    the mines among the unopened cells, using the numbers.
    """
    # The field X is not read: the unopened cells are the -1 entries of game_data.
    board = instance["game_data"]  # board[r][c]: the number on cell (r, c), or -1 if the cell is unopened
    rows, cols = len(board), len(board[0])  # the size of the board, taken from the data
    unopened = np.array(board) == -1  # True where the cell is unopened

    model = Model("minesweeper")

    # mine[r, c] is 1 when cell (r, c) holds a mine, and 0 when it does not
    mine = model.addMatrixVar((rows, cols), vtype="B", name="mine")

    # An opened cell is safe (the player opened it without hitting a mine), so a
    # mine can only be on an unopened cell. This is an assumption from the rules of
    # the game, not something the numbers themselves show.
    model.addMatrixCons(mine <= unopened.astype(int))

    # The number on each opened cell is the count of mines among its neighbours.
    for r in range(rows):
        for c in range(cols):
            if not unopened[r, c]:
                neighbours = [mine[i, j]
                              for i in range(max(r - 1, 0), min(r + 2, rows))
                              for j in range(max(c - 1, 0), min(c + 2, cols))
                              if (i, j) != (r, c)]
                model.addCons(quicksum(neighbours) == board[r][c])

    # No objective is set: any placement of mines that fits every number is an answer.
    return model, {"mines": mine}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
