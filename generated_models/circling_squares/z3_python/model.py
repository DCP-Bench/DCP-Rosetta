# circling_squares: a Z3 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/circling_squares.html
# Run it (after `pip install z3-solver numpy`) with:
#   python circling_squares.py

import z3


# The squares of x1 and x2 add up to the same as the squares of y1 and y2.
def same_square_sum(x1, x2, y1, y2):
    return x1 * x1 + x2 * x2 == y1 * y1 + y2 * y2


def create_model(instance):
    """Ten squares are arranged in a circle, labelled A B C D E F G H I K in order. Put a
    different number in each square so that any two adjacent squares have the same sum of
    squares as the two squares opposite them."""
    # the numbers in the ten squares, in circular order
    A, B, C, D, E, F, G, H, I, K = squares = z3.Ints("A B C D E F G H I K")

    solver = z3.Solver()

    # Each square holds a whole number from 1 to 99, as no number needs more than two figures.
    solver.add([z3.And(v >= 1, v <= 99) for v in squares])

    # No two squares hold the same number.
    solver.add(z3.Distinct(squares))

    # The four numbers given in the puzzle stand as they are.
    solver.add(A == 16, B == 2, F == 8, G == 14)

    # Each pair of adjacent squares has the same sum of squares as the pair opposite it.
    solver.add(
        same_square_sum(A, B, F, G),
        same_square_sum(B, C, G, H),
        same_square_sum(C, D, H, I),
        same_square_sum(D, E, I, K),
        same_square_sum(E, F, K, A),
    )

    return solver, {"A": A, "B": B, "C": C, "D": D, "E": E,
                    "F": F, "G": G, "H": H, "I": I, "K": K}


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
