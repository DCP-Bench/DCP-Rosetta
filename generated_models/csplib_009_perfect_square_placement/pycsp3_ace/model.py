# csplib_009_perfect_square_placement: a PyCSP3 model from DCP Rosetta.
# Download the `csplib_009_perfect_square_placement.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_009_perfect_square_placement.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python csplib_009_perfect_square_placement.py csplib_009_perfect_square_placement.json

from pycsp3 import *


def create_model(instance):
    """Pack a set of squares with the given integer sides into a bigger square of side base,
    so that no squares overlap and all square borders are parallel to the border of the big
    square. The squares fill the big square with no spare capacity."""
    base = instance["base"]  # the side of the big square
    sides = instance["sides"]  # sides[i] is the side of square i
    n_squares = len(sides)

    # x_coords[i] is the left edge of square i, counted from 0; the square must fit in the big square
    x_coords = VarArray(size=n_squares, dom=lambda i: range(base - sides[i] + 1))
    # y_coords[i] is the bottom edge of square i, counted from 0; the square must fit in the big square
    y_coords = VarArray(size=n_squares, dom=lambda i: range(base - sides[i] + 1))

    # the pairs of squares i < j with equal sides, which can swap places with each other
    equal_pairs = [(i, j) for i in range(n_squares) for j in range(i + 1, n_squares) if sides[i] == sides[j]]

    satisfy(
        # no two squares overlap: each square is a rectangle of its side in both directions
        NoOverlap(
            origins=[[x_coords[i], y_coords[i]] for i in range(n_squares)],
            lengths=[[sides[i], sides[i]] for i in range(n_squares)],
        ),
        # redundant, implied by the no-overlap: the squares crossing any column have disjoint
        # heights inside the big square, so their sides add up to at most base
        Cumulative(origins=x_coords, lengths=sides, heights=sides) <= base,
        # redundant, implied by the no-overlap: the same for the rows, the squares crossing any row
        Cumulative(origins=y_coords, lengths=sides, heights=sides) <= base,
        # symmetry breaking, not in the description: two squares of equal side can swap places, so
        # the one with the smaller index is kept the further left (or level). Solutions that differ
        # only by swapping equal squares are therefore not reported, but a solution always remains.
        [x_coords[i] <= x_coords[j] for i, j in equal_pairs],
    )

    return {"x_coords": x_coords, "y_coords": y_coords}


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
