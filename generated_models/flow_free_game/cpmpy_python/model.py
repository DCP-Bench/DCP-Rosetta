# flow_free_game: a CPMpy model from DCP Rosetta.
# Download the `flow_free_game.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/flow_free_game.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python flow_free_game.py flow_free_game.json

import cpmpy as cp
import numpy as np


def create_model(instance):
    """Flow Free: connect matching colours with pipes and cover the entire board.
    Every cell gets a colour, and each colour forms one pipe between its two end cells."""
    board = np.array(instance["board"])  # board[i][j]: colour of an end cell, or 0 for an empty cell
    rows, cols = board.shape
    n_colors = int(board.max())  # colours are numbered 1..n_colors

    # B[i, j] is the colour of the pipe through cell (i, j); every cell gets a colour.
    B = cp.intvar(1, n_colors, shape=(rows, cols), name="B")

    model = cp.Model()

    for i in range(rows):
        for j in range(cols):
            # Orthogonal neighbours of the cell.
            neighbours = [(k, l) for k, l in ((i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1))
                          if 0 <= k < rows and 0 <= l < cols]
            # Number of neighbours that carry the same colour as this cell.
            same_colour_neighbours = cp.sum([B[i, j] == B[k, l] for k, l in neighbours])

            if board[i, j] != 0:
                # An end cell keeps its colour and joins exactly one neighbour of that colour:
                # the pipe starts here.
                model.add(B[i, j] == board[i, j])
                model.add(same_colour_neighbours == 1)
            else:
                # A cell in the middle of a pipe has exactly two neighbours of its colour:
                # the pipe comes in from one and leaves through the other.
                model.add(same_colour_neighbours == 2)

    return model, {"B": B}


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
