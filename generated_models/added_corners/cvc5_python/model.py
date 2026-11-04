# added_corners: a cvc5 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/added_corners.html
# Run it (after `pip install cvc5 numpy`) with:
#   python added_corners.py

import cvc5.pythonic as c5


def create_model(instance):
    """Enter the digits 1 through 8 in the circles and squares of a ring such that
    the number in each square is equal to the sum of the adjoining circles."""
    # positions[i] is the digit in cell i, reading the layout left to right and top
    # to bottom, skipping the empty centre.
    positions = [c5.Int(f"position_{i}") for i in range(8)]
    # Cells 0, 2, 5 and 7 are the corner circles; cells 1, 3, 4 and 6 are the squares
    # at the edge midpoints.
    a, b, c, d, e, f, g, h = positions

    solver = c5.Solver()

    # Each entry is a digit from 1 to 8.
    solver.add([c5.And(p >= 1, p <= 8) for p in positions])
    # The digits are all different, so each one is used once.
    solver.add(c5.Distinct(positions))
    # Each square holds the sum of the two circles next to it.
    solver.add(
        b == a + c,  # top square
        d == a + f,  # left square
        e == c + h,  # right square
        g == f + h,  # bottom square
    )
    return solver, {"positions": positions}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
