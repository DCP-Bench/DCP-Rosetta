# knights_tour: a PyCSP3 model from DCP Rosetta.
# Download the `knights_tour.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/knights_tour.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python knights_tour.py knights_tour.json

from pycsp3 import *


def create_model(instance):
    """Find a knight's tour of an n by n chessboard: a sequence of knight moves that visits
    every square exactly once, numbering the squares 0 to n * n - 1 in visiting order.
    The tour does not have to return to its starting square."""
    n = instance["n"]              # the chessboard has n rows and n columns
    n_squares = n * n              # the squares are numbered 0 to n_squares - 1, row by row

    # move[s] is the move number at which the knight visits square s
    move = VarArray(size=n_squares, dom=range(n_squares), id="move")
    # square[k] is the square the knight visits at move k (the inverse of move)
    square = VarArray(size=n_squares, dom=range(n_squares), id="square")

    # a knight's move changes the row by 1 and the column by 2, or the row by 2 and the column by 1
    knight_moves = [
        (a, b)
        for a in range(n_squares)
        for b in range(n_squares)
        if abs(a // n - b // n) * abs(a % n - b % n) == 2
    ]

    satisfy(
        # every square gets exactly one move number
        AllDifferent(move),
        # the move numbers are the inverse of the squares visited
        Channel(move, square),
        # the knight visits every square exactly once (implied by Channel, kept for propagation)
        AllDifferent(square),
        # each move goes from one square to a square a knight's move away
        [Table(scope=(square[k], square[k + 1]), supports=knight_moves) for k in range(n_squares - 1)],
    )

    # x[i] lists the move numbers of row i of the board
    return {"x": [move[i * n:(i + 1) * n] for i in range(n)]}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())
