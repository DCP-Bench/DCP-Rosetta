# csplib_014_solitaire_battleships: a PyCSP3 model from DCP Rosetta.
# Download the `csplib_014_solitaire_battleships.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_014_solitaire_battleships.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python csplib_014_solitaire_battleships.py csplib_014_solitaire_battleships.json

from pycsp3 import *


def create_model(instance):
    """Solitaire Battleships: place the fleet on a grid. Battleships are four squares long, cruisers
    three, destroyers two and submarines one square. Ships are horizontal or vertical, and no two
    ships touch, not even diagonally. The numbers along the right side and below the grid give the
    number of occupied squares in each row and column. Some squares are given as hints."""
    n_rows = instance["rows"]         # the number of rows
    n_cols = instance["cols"]         # the number of columns
    # rowsum[k] and colsum[k]: the number of occupied squares in row k and column k of the grid, numbered from 0.
    rowsum = instance["rowsum"]
    colsum = instance["colsum"]
    # hints is a list of [row, col, code] triples: a given square, numbered from 0, with its cell code.
    hints = instance["hints"]
    # fleet_counts is a list of [size, count] pairs: count ships with that many squares.
    ship_count = {size: count for size, count in instance["fleet_counts"]}

    # The cell codes, as the instance gives them.
    WATER = instance["WATER"]     # an empty square
    CIRCLE = instance["CIRCLE"]   # a submarine
    LEFT = instance["LEFT"]       # the left end of a horizontal ship
    RIGHT = instance["RIGHT"]     # the right end of a horizontal ship
    TOP = instance["TOP"]         # the top end of a vertical ship
    BOTTOM = instance["BOTTOM"]   # the bottom end of a vertical ship
    MIDDLE = instance["MIDDLE"]   # a square of a ship between its two ends

    # The grid is framed by a border of water squares, so that every square has all eight neighbours.
    # board[r][c] is the cell code of the square in row r and column c of the framed grid.
    board = VarArray(size=[n_rows + 2, n_cols + 2], dom=[WATER, CIRCLE, LEFT, RIGHT, TOP, BOTTOM, MIDDLE])
    rows = range(1, n_rows + 1)   # the rows of the puzzle grid inside the frame
    cols = range(1, n_cols + 1)   # the columns of the puzzle grid inside the frame

    satisfy(
        # The border squares are water.
        (board[r][c] == WATER
         for r in range(n_rows + 2)
         for c in range(n_cols + 2)
         if r in (0, n_rows + 1) or c in (0, n_cols + 1)),

        # The given squares of the puzzle, shifted by one for the frame.
        (board[r + 1][c + 1] == code for r, c, code in hints),

        # A submarine is alone: all four orthogonal neighbours are water.
        (imply(board[r][c] == CIRCLE,
               And(board[r - 1][c] == WATER, board[r + 1][c] == WATER,
                   board[r][c - 1] == WATER, board[r][c + 1] == WATER))
         for r in rows
         for c in cols),

        # A left end has water above, below and to its left, and a middle or right square to its right.
        (imply(board[r][c] == LEFT,
               And(board[r - 1][c] == WATER, board[r + 1][c] == WATER,
                   board[r][c - 1] == WATER,
                   board[r][c + 1].among(MIDDLE, RIGHT)))
         for r in rows
         for c in cols),

        # A right end has water above, below and to its right, and a left or middle square to its left.
        (imply(board[r][c] == RIGHT,
               And(board[r - 1][c] == WATER, board[r + 1][c] == WATER,
                   board[r][c + 1] == WATER,
                   board[r][c - 1].among(LEFT, MIDDLE)))
         for r in rows
         for c in cols),

        # A top end has water to its left, right and above, and a middle or bottom square below it.
        (imply(board[r][c] == TOP,
               And(board[r - 1][c] == WATER, board[r][c - 1] == WATER,
                   board[r][c + 1] == WATER,
                   board[r + 1][c].among(MIDDLE, BOTTOM)))
         for r in rows
         for c in cols),

        # A bottom end has water to its left, right and below, and a top or middle square above it.
        (imply(board[r][c] == BOTTOM,
               And(board[r + 1][c] == WATER, board[r][c - 1] == WATER,
                   board[r][c + 1] == WATER,
                   board[r - 1][c].among(TOP, MIDDLE)))
         for r in rows
         for c in cols),

        # A middle square lies in a horizontal ship (left and right neighbours are ship squares, above and below
        # water) or in a vertical ship (above and below are ship squares, left and right water).
        (imply(board[r][c] == MIDDLE,
               Or(And(board[r][c - 1].among(LEFT, MIDDLE),
                      board[r][c + 1].among(MIDDLE, RIGHT),
                      board[r - 1][c] == WATER, board[r + 1][c] == WATER),
                  And(board[r - 1][c].among(TOP, MIDDLE),
                      board[r + 1][c].among(MIDDLE, BOTTOM),
                      board[r][c - 1] == WATER, board[r][c + 1] == WATER)))
         for r in rows
         for c in cols),

        # No two ships touch, not even diagonally: every diagonal neighbour of a ship square is water.
        (imply(board[r][c] != WATER,
               And(board[r - 1][c - 1] == WATER, board[r - 1][c + 1] == WATER,
                   board[r + 1][c - 1] == WATER, board[r + 1][c + 1] == WATER))
         for r in rows
         for c in cols),

        # Fleet: ship_count[size] ships of each size. The ships are counted by their parts, since a ship is not a variable.
        # Submarines are the one-square ships, each shown as a CIRCLE square.
        Sum(board[r][c] == CIRCLE for r in rows for c in cols) == ship_count[1],
        # Every ship of two or more squares has exactly one end on the left or top, so the left and top ends
        # together count the ships of sizes 2, 3 and 4.
        Sum(board[r][c] == LEFT for r in rows for c in cols)
        + Sum(board[r][c] == TOP for r in rows for c in cols)
        == ship_count[2] + ship_count[3] + ship_count[4],
        # Only a battleship has two adjacent middle squares, so each adjacent pair of middle squares, horizontal
        # or vertical, is one battleship.
        Sum(And(board[r][c] == MIDDLE, board[r][c - 1] == MIDDLE) for r in rows for c in cols)
        + Sum(And(board[r][c] == MIDDLE, board[r - 1][c] == MIDDLE) for r in rows for c in cols)
        == ship_count[4],
        # Ships of size 3 and 4 are exactly those with a middle square next to their left or top end.
        Sum(And(board[r][c] == MIDDLE, board[r][c - 1] == LEFT) for r in rows for c in cols)
        + Sum(And(board[r][c] == MIDDLE, board[r - 1][c] == TOP) for r in rows for c in cols)
        == ship_count[3] + ship_count[4],

        # The row and column sums count the occupied squares, submarines included. Framed row r is row r - 1
        # of the puzzle, and likewise for the columns.
        (Sum(board[r][c] != WATER for c in cols) == rowsum[r - 1]
         for r in rows),
        (Sum(board[r][c] != WATER for r in rows) == colsum[c - 1]
         for c in cols),
    )

    # The puzzle grid: the board without its frame of water.
    grid = [[board[r][c] for c in cols] for r in rows]
    return {"grid": grid}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        print("grid", "=")
        for row in outputs["grid"]:
            print(values(row))
    else:
        print("No solution:", status())
