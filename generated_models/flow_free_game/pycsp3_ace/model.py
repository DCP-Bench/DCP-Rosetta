# flow_free_game: a PyCSP3 model from DCP Rosetta.
# Download the `flow_free_game.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/flow_free_game.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python flow_free_game.py flow_free_game.json

from pycsp3 import *


def create_model(instance):
    """Connect the matching numbered cells of a board with pipes, so that the pipes cover
    the whole board and do not cross or overlap. Colour every cell with colours 1 to 5,
    keeping the numbered cells in their colour: a numbered cell has exactly one
    neighbour (horizontal or vertical) of its own colour, and every other cell has
    exactly two."""
    board = instance["board"]  # board[r][c] is the colour of the numbered cell (r, c), 0 for an empty cell
    n = len(board)
    n_colors = 5  # the statement's colours 1 to 5
    pipe_end_neighbours = 1  # a numbered cell has exactly one neighbour of its own colour
    pipe_middle_neighbours = 2  # an empty cell has exactly two neighbours of its own colour

    # cell_color[r][c] is the colour of the cell in row r and column c.
    cell_color = VarArray(size=[n, n], dom=range(1, n_colors + 1))

    def neighbours(r, c):
        """The cells next to (r, c) horizontally or vertically, inside the board."""
        steps = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        return [(r + dr, c + dc) for dr, dc in steps
                if 0 <= r + dr < n and 0 <= c + dc < n]

    def same_colour_neighbours(r, c):
        """The number of neighbours of (r, c) that have the same colour as (r, c)."""
        return Sum(cell_color[r][c] == cell_color[nr][nc] for nr, nc in neighbours(r, c))

    # The statement's rule is the neighbour count alone, so it does not forbid a closed loop of one colour that contains no numbered cell.
    satisfy(
        # A numbered cell keeps its given colour.
        [cell_color[r][c] == board[r][c] for r in range(n) for c in range(n)
         if board[r][c] != 0],
        # A numbered cell has exactly one neighbour of its own colour, the other end of its pipe.
        [same_colour_neighbours(r, c) == pipe_end_neighbours
         for r in range(n) for c in range(n) if board[r][c] != 0],
        # An empty cell has exactly two neighbours of its own colour, so its pipe runs through it.
        [same_colour_neighbours(r, c) == pipe_middle_neighbours
         for r in range(n) for c in range(n) if board[r][c] == 0],
    )

    return {"B": cell_color}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        print("B", "=")
        for row in outputs["B"]:
            print(values(row))
    else:
        print("No solution:", status())
