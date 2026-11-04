# added_corners: a hermax (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/added_corners.html
# Run it (after `pip install hermax`) with:
#   python added_corners.py

from hermax.model import Model


def create_model(instance):
    """Put the digits 1 through 8 in the eight places of a 3 by 3 square without its centre,
    so that each side place (a square) holds the sum of the two corner places (circles)
    next to it. The puzzle has no instance data: the digits and the shape of the square are
    part of the statement, so `instance` is not read."""
    n = 8  # the digits 1..n, one per place

    m = Model()

    # Places are numbered like reading a book:
    #   a b c
    #   d   e
    #   f g h
    # positions[0..7] is the digit in a, b, c, d, e, f, g, h in that order.
    positions = m.int_vector("positions", n, 1, n)
    a, b, c, d, e, f, g, h = (positions[i] for i in range(n))

    # Each digit 1 through 8 is used exactly once.
    m &= positions.all_different()

    # Top side: the square b is the sum of the circles a and c next to it.
    m &= (b == a + c)
    # Left side: the square d is the sum of the circles a and f next to it.
    m &= (d == a + f)
    # Right side: the square e is the sum of the circles c and h next to it.
    m &= (e == c + h)
    # Bottom side: the square g is the sum of the circles f and h next to it.
    m &= (g == f + h)

    # Satisfaction problem: there is no objective to minimise or maximise.
    # The outputs are the eight digits, read left to right, top to bottom.
    return m, {"positions": positions}


if __name__ == "__main__":
    model, outputs = create_model({})
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
