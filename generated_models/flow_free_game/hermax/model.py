# flow_free_game: a hermax (Python) model from DCP Rosetta.
# Download the `flow_free_game.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/flow_free_game.html
# Then run it on the first instance (after `pip install hermax`):
#   python flow_free_game.py flow_free_game.json

from hermax.model import Model


def create_model(instance):
    """Flow Free: give every cell of the board a pipe colour so that each clue cell has
    exactly one neighbouring cell of its own colour (a pipe end) and each empty cell has
    exactly two (a pipe passing through). Only this local degree rule is enforced, so a
    closed loop of a colour detached from that colour's pipe is not excluded."""
    board = instance["board"]  # board[i][j]: clue colour of cell (i, j), 0 if the cell is empty
    rows, cols = len(board), len(board[0])  # board height and width
    # Each colour has a pair of clue cells, so the colours are 1..the largest clue colour.
    n_colours = max(max(row) for row in board)

    m = Model()
    # B[i][j] is the pipe colour of cell (i, j), from 1 to n_colours
    B = m.int_matrix("B", rows, cols, 1, n_colours)

    # A clue cell keeps its own colour.
    for i in range(rows):
        for j in range(cols):
            if board[i][j] != 0:
                m &= (B[i][j] == board[i][j])

    # same[(a, b)] is true when the neighbouring cells a and b have the same colour
    same = {}
    for i in range(rows):
        for j in range(cols):
            for k, l in ((i + 1, j), (i, j + 1)):
                if k < rows and l < cols:
                    same_colour = m.bool(f"same_{i}_{j}_{k}_{l}")
                    m &= (B[i][j] == B[k][l]).iff(same_colour)
                    same[(i, j), (k, l)] = same_colour
                    same[(k, l), (i, j)] = same_colour

    for i in range(rows):
        for j in range(cols):
            # the neighbours of cell (i, j) that are on the same pipe colour
            same_neighbours = [same[(i, j), (k, l)] for k, l in
                               ((i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1))
                               if 0 <= k < rows and 0 <= l < cols]
            if board[i][j] != 0:
                # clue cell: exactly one neighbour of its own colour
                m &= (sum(same_neighbours) == 1)
            else:
                # empty cell: exactly two neighbours of its own colour
                m &= (sum(same_neighbours) == 2)

    return m, {"B": B}


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
