# added_corners: a CPMpy model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/added_corners.html
# Run it (after `pip install cpmpy`) with:
#   python added_corners.py

import cpmpy as cp


def create_model(instance):
    """Enter the digits 1 through 8 in the circles and squares of a ring such that
    the number in each square is equal to the sum of the adjoining circles."""
    # The puzzle states its own size and layout, so the instance holds no data.

    # positions[i] is the digit in cell i, reading the 3x3 ring like a book (left to
    # right, top to bottom), skipping the empty middle:  C S C / S _ S / C S C
    positions = cp.intvar(1, 8, shape=8, name="positions")
    # Cells 0, 2, 5 and 7 are circles; cells 1, 3, 4 and 6 are squares.
    a, b, c, d, e, f, g, h = positions

    model = cp.Model()
    # Each digit is used once.
    model.add(cp.AllDifferent(positions))
    # Each square is the sum of the two circles next to it.
    model.add(b == a + c)  # top square
    model.add(d == a + f)  # left square
    model.add(e == c + h)  # right square
    model.add(g == f + h)  # bottom square

    return model, {"positions": positions}


if __name__ == "__main__":
    model, outputs = create_model({})
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
