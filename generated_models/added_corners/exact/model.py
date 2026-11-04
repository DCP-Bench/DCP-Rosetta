# added_corners: an Exact (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/added_corners.html
# Run it (after `pip install exact numpy`) with:
#   python added_corners.py

from exact import Exact


def create_model(instance):
    """Enter the digits 1 through 8 in the circles and squares of a frame such that
    the number in each square is equal to the sum of the numbers in the adjoining circles."""
    n_digits = 8  # the digits 1 to 8, one for each cell of the frame

    solver = Exact()

    # Exact identifies its variables by name.
    # The digit in each cell of the frame. a, c, f and h are circles; b, d, e and g are squares.
    positions = [f"position_{i}" for i in range(n_digits)]
    for name in positions:
        solver.addVariable(name, 1, n_digits)
    a, b, c, d, e, f, g, h = positions

    # is_digit[i][v - 1] is 1 when cell i holds the digit v.
    is_digit = [[f"position_{i}_is_{v}" for v in range(1, n_digits + 1)] for i in range(n_digits)]
    for i in range(n_digits):
        for name in is_digit[i]:
            solver.addVariable(name, 0, 1)
        # Each cell holds exactly one digit, and the cell shows that digit.
        solver.addConstraint([(1, name) for name in is_digit[i]], True, 1, True, 1)
        solver.addConstraint([(v, is_digit[i][v - 1]) for v in range(1, n_digits + 1)]
                             + [(-1, positions[i])], True, 0, True, 0)

    # Each digit is in exactly one cell.
    for v in range(1, n_digits + 1):
        solver.addConstraint([(1, is_digit[i][v - 1]) for i in range(n_digits)], True, 1, True, 1)

    # Each square holds the sum of the two circles next to it.
    solver.addConstraint([(1, b), (-1, a), (-1, c)], True, 0, True, 0)  # top square
    solver.addConstraint([(1, d), (-1, a), (-1, f)], True, 0, True, 0)  # left square
    solver.addConstraint([(1, e), (-1, c), (-1, h)], True, 0, True, 0)  # right square
    solver.addConstraint([(1, g), (-1, f), (-1, h)], True, 0, True, 0)  # bottom square

    return solver, {"positions": positions}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
