# flow_free_game: an Exact (Python) model from DCP Rosetta.
# Download the `flow_free_game.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/flow_free_game.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python flow_free_game.py flow_free_game.json

from exact import Exact


def create_model(instance):
    """Flow Free: colour every cell of the board, so that each colour forms one pipe running
    between the two cells given that colour, and the pipes cover the whole board."""
    board = instance["board"]  # board[i][j]: the colour of cell (i, j), or 0 when the cell is empty
    n_rows, n_cols = len(board), len(board[0])  # the size of the board
    n_colours = max(max(row) for row in board)  # the number of colours, the largest colour on the board
    colours = range(1, n_colours + 1)  # the colour numbers

    solver = Exact()

    # Exact identifies its variables by name.
    # B[i][j] is the colour of cell (i, j)
    B = [[f"B_{i}_{j}" for j in range(n_cols)] for i in range(n_rows)]
    # is_colour[i][j][c] is 1 when cell (i, j) has colour c, and 0 when not
    is_colour = [[{c: f"B_{i}_{j}_is_{c}" for c in colours} for j in range(n_cols)]
                 for i in range(n_rows)]
    for i in range(n_rows):
        for j in range(n_cols):
            solver.addVariable(B[i][j], 1, n_colours)
            for c in colours:
                solver.addVariable(is_colour[i][j][c], 0, 1)

    # edges: each pair of neighbouring cells on the board, listed once
    edges = [(i, j, k, l) for i in range(n_rows) for j in range(n_cols)
             for k, l in ((i + 1, j), (i, j + 1)) if k < n_rows and l < n_cols]
    # same[(i, j, k, l)] is 1 when the neighbouring cells (i, j) and (k, l) have the same colour
    same = {}
    for i, j, k, l in edges:
        same[(i, j, k, l)] = same[(k, l, i, j)] = f"same_{i}_{j}_{k}_{l}"
        solver.addVariable(same[(i, j, k, l)], 0, 1)

    # A cell has exactly one colour, and B[i][j] is that colour.
    for i in range(n_rows):
        for j in range(n_cols):
            solver.addConstraint([(1, is_colour[i][j][c]) for c in colours], True, 1, True, 1)
            solver.addConstraint([(c, is_colour[i][j][c]) for c in colours] + [(-1, B[i][j])],
                                 True, 0, True, 0)
            # A cell given a colour keeps that colour.
            if board[i][j] != 0:
                solver.addConstraint([(1, is_colour[i][j][board[i][j]])], True, 1, True, 1)

    # Each same flag follows the colours of its two cells.
    for i, j, k, l in edges:
        for c in colours:
            here, there = is_colour[i][j][c], is_colour[k][l][c]
            solver.addConstraint([(1, same[(i, j, k, l)]), (-1, here), (-1, there)], True, -1)
            solver.addConstraint([(1, same[(i, j, k, l)]), (1, here), (-1, there)], False, 0, True, 1)
            solver.addConstraint([(1, same[(i, j, k, l)]), (-1, here), (1, there)], False, 0, True, 1)

    # A cell given a colour is a pipe end, and has exactly one neighbour of its colour. Any other
    # cell has exactly two.
    for i in range(n_rows):
        for j in range(n_cols):
            neighbours = [(k, l) for k, l in ((i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1))
                          if 0 <= k < n_rows and 0 <= l < n_cols]  # the cells next to (i, j)
            n_same = 1 if board[i][j] != 0 else 2  # how many neighbours of its colour the cell has
            solver.addConstraint([(1, same[(i, j, k, l)]) for k, l in neighbours],
                                 True, n_same, True, n_same)

    return solver, {"B": B}


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
