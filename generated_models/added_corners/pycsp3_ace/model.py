# added_corners: a PyCSP3 model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/added_corners.html
# Run it (after `pip install pycsp3`, which also needs Java for its ACE solver) with:
#   python added_corners.py

from pycsp3 import *


def create_model(instance):
    """Enter the digits 1 through 8 into the eight positions around the edge of a
    3 by 3 grid with an empty centre, each digit exactly once. Corners are circles,
    middles of the sides are squares; the number in each square is the sum of the
    two circles adjoining it."""
    # the digits 1 through n_digits go into the positions around the edge
    n_digits = 8

    # positions[k] is the digit in the k-th position in reading order:
    # 0 top left, 1 top middle, 2 top right, 3 middle left, 4 middle right,
    # 5 bottom left, 6 bottom middle, 7 bottom right.
    positions = VarArray(size=n_digits, dom=range(1, n_digits + 1))

    satisfy(
        # Each digit is used exactly once.
        AllDifferent(positions),
        # The top middle square is the sum of the top left and top right circles.
        positions[1] == positions[0] + positions[2],
        # The middle left square is the sum of the top left and bottom left circles.
        positions[3] == positions[0] + positions[5],
        # The middle right square is the sum of the top right and bottom right circles.
        positions[4] == positions[2] + positions[7],
        # The bottom middle square is the sum of the bottom left and bottom right circles.
        positions[6] == positions[5] + positions[7],
    )

    return {"positions": positions}


if __name__ == "__main__":
    outputs = create_model({})
    if solve() is SAT:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())
