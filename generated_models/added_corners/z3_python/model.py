# added_corners: a Z3 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/added_corners.html
# Run it (after `pip install z3-solver numpy`) with:
#   python added_corners.py

import z3


def create_model(instance):
    """Enter the digits 1 through 8 in the circles and squares of a ring such that
    the number in each square is equal to the sum of the adjoining circles."""
    # The puzzle states its own size and layout, so the instance holds no data.

    # positions[i] is the digit in cell i, reading the ring like a book (left to right,
    # top to bottom), skipping the empty middle:  C S C / S _ S / C S C
    positions = [z3.Int(f"positions_{i}") for i in range(8)]
    # Cells 0, 2, 5 and 7 are circles; cells 1, 3, 4 and 6 are squares.
    a, b, c, d, e, f, g, h = positions

    solver = z3.Solver()

    # Each cell holds a digit from 1 to 8.
    solver.add([z3.And(1 <= p, p <= 8) for p in positions])

    # Each digit is used once.
    solver.add(z3.Distinct(positions))

    # Each square is the sum of the two circles next to it.
    solver.add(b == a + c)  # top square
    solver.add(d == a + f)  # left square
    solver.add(e == c + h)  # right square
    solver.add(g == f + h)  # bottom square

    return solver, {"positions": positions}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
