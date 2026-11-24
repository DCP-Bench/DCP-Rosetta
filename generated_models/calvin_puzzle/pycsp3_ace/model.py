# calvin_puzzle: a PyCSP3 model from DCP Rosetta.
# Download the `calvin_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/calvin_puzzle.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python calvin_puzzle.py calvin_puzzle.json

from pycsp3 import *


def create_model(instance):
    """Fill an n by n grid with the numbers 1 to n^2, each once. Each number follows the
    previous one by one of two moves: horizontally or vertically, exactly three squares away
    (a gap of two squares), or diagonally, exactly two squares away (a gap of one square).
    Find the completed grid."""
    n = instance["n"]   # n: the grid has n rows and n columns
    n_squares = n * n   # the number of squares, which hold the numbers 1 to n^2

    # square[k] is the square (row * n + column) that holds number k + 1
    square = VarArray(size=n_squares, dom=range(n_squares))
    # row[k] and col[k] are the row and the column of number k + 1
    row = VarArray(size=n_squares, dom=range(n))
    col = VarArray(size=n_squares, dom=range(n))
    # grid[s] is the number written in square s, in row-major order
    grid = VarArray(size=n_squares, dom=range(1, n_squares + 1))

    satisfy(
        # Every number sits on a square of its own.
        AllDifferent(square),
        # The square of number k + 1 is its row and column in the row-major numbering.
        [square[k] == row[k] * n + col[k] for k in range(n_squares)],
        # Square square[k] holds number k + 1.
        [grid[square[k]] == k + 1 for k in range(n_squares)],
        # Each number after the first is reached from the previous one by a move of type I
        # (horizontal or vertical, three squares away) or type II (diagonal, two squares away).
        [
            Or(
                And(row[k + 1] == row[k], abs(col[k + 1] - col[k]) == 3),
                And(col[k + 1] == col[k], abs(row[k + 1] - row[k]) == 3),
                And(abs(row[k + 1] - row[k]) == 2, abs(col[k + 1] - col[k]) == 2),
            )
            for k in range(n_squares - 1)
        ],
    )

    # The completed grid, one list per row.
    return {"x": [[grid[r * n + c] for c in range(n)] for r in range(n)]}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        print("x", "=")
        for row in outputs["x"]:
            print(values(row))
    else:
        print("No solution:", status())
