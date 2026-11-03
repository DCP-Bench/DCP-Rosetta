# flow_free_game: a Z3 (Python) model from DCP Rosetta.
# Download the `flow_free_game.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/flow_free_game.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python flow_free_game.py flow_free_game.json

import z3


def create_model(instance):
    """Flow Free: colour every cell of the board so that each colour forms one pipe joining
    its two given end cells, the pipes do not cross or overlap, and the whole board is covered.
    A pipe is a chain of orthogonally adjacent cells of one colour."""
    board = instance["board"]                  # board[i][j]: the colour of cell (i, j), or 0 if it is empty
    n_rows = len(board)                        # number of rows
    n_cols = len(board[0])                     # number of columns
    n_colors = max(max(row) for row in board)  # the colours are numbered 1 to n_colors

    # colour[i][j] is the colour of the pipe through cell (i, j)
    colour = [[z3.Int(f"colour_{i}_{j}") for j in range(n_cols)] for i in range(n_rows)]

    solver = z3.Solver()

    # Every cell has one of the colours 1 to n_colors.
    for i in range(n_rows):
        for j in range(n_cols):
            solver.add(colour[i][j] >= 1)
            solver.add(colour[i][j] <= n_colors)

    for i in range(n_rows):
        for j in range(n_cols):
            # The orthogonal neighbours of cell (i, j) that lie on the board.
            neighbours = [(a, b) for a, b in ((i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1))
                          if 0 <= a < n_rows and 0 <= b < n_cols]
            # How many of those neighbours have the same colour as the cell.
            same = z3.Sum([z3.If(colour[i][j] == colour[a][b], 1, 0) for a, b in neighbours])
            if board[i][j] != 0:
                # An end cell has its given colour and is joined to exactly one neighbour of that colour.
                solver.add(colour[i][j] == board[i][j])
                solver.add(same == 1)
            else:
                # A cell in the middle of a pipe is joined to exactly two neighbours of its colour.
                solver.add(same == 2)

    return solver, {"B": colour}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
