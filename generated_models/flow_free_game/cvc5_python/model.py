# flow_free_game: a cvc5 (Python) model from DCP Rosetta.
# Download the `flow_free_game.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/flow_free_game.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python flow_free_game.py flow_free_game.json

import cvc5.pythonic as c5


def create_model(instance):
    """Flow Free: connect the two cells of each color with a pipe, so that the pipes
    cover the whole board without crossing or overlapping. Every cell gets a color
    from 1 to n_colors."""
    board = instance["board"]                  # board[i][j]: the color given to cell (i, j), or 0 if the cell is empty
    n_rows = len(board)                        # the number of rows
    n_cols = len(board[0])                     # the number of columns
    n_cells = n_rows * n_cols                  # the number of cells
    n_colors = max(max(row) for row in board)  # the colors are numbered 1 to n_colors

    # color[i][j] is the color of cell (i, j)
    color = [[c5.Int(f"color_{i}_{j}") for j in range(n_cols)] for i in range(n_rows)]
    # rank[i][j] counts the steps from the end of the pipe to cell (i, j)
    rank = [[c5.Int(f"rank_{i}_{j}") for j in range(n_cols)] for i in range(n_rows)]

    # The cells orthogonally next to cell (i, j).
    def neighbours(i, j):
        cells = []
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ni, nj = i + di, j + dj
            if 0 <= ni < n_rows and 0 <= nj < n_cols:
                cells.append((ni, nj))
        return cells

    solver = c5.Solver()

    # Every cell takes a color from 1 to n_colors, and a given cell keeps its color.
    for i in range(n_rows):
        for j in range(n_cols):
            solver.add(color[i][j] >= 1)
            solver.add(color[i][j] <= n_colors)
            if board[i][j] != 0:
                solver.add(color[i][j] == board[i][j])

    # Each color is one pipe. An end cell has exactly one neighbor of its color, and every
    # other cell has exactly two, so the pipe runs through it.
    for i in range(n_rows):
        for j in range(n_cols):
            same = [c5.If(color[ki][kj] == color[i][j], 1, 0) for ki, kj in neighbours(i, j)]
            solver.add(c5.Sum(same) == (1 if board[i][j] != 0 else 2))

    # Every cell has a step count from 0 to n_cells - 1. An empty cell is never at an end, so its
    # step count is at least 1. A cell with a step count above 0 has a neighbor of its color one
    # step closer to the end. Step counts fall along the pipe, so the pipe cannot form a loop.
    for i in range(n_rows):
        for j in range(n_cols):
            solver.add(rank[i][j] >= 0)
            solver.add(rank[i][j] <= n_cells - 1)
            if board[i][j] == 0:
                solver.add(rank[i][j] >= 1)
            closer = [
                c5.And(color[ki][kj] == color[i][j], rank[ki][kj] == rank[i][j] - 1)
                for ki, kj in neighbours(i, j)
            ]
            solver.add(c5.Implies(rank[i][j] > 0, c5.Or(closer)))

    # The color of each cell, row by row.
    B = [[color[i][j] for j in range(n_cols)] for i in range(n_rows)]
    return solver, {"B": B}


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
