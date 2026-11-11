# circling_squares: a PyCSP3 model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/circling_squares.html
# Run it (after `pip install pycsp3`, which also needs Java for its ACE solver) with:
#   python circling_squares.py

from pycsp3 import *


def create_model(instance):
    """Place a different number in each of ten squares on a circle so that the sum of the
    squares of any two adjacent numbers equals the sum of the squares of the two numbers
    diametrically opposite them. The numbers A=16, B=2, F=8 and G=14 are given. Fractions
    are not allowed, and no number needs more than two figures."""
    n_squares = 10  # the ten squares on the circle, A B C D E F G H I K in order
    half = n_squares // 2  # the square diametrically opposite square p is p + half
    max_number = 99  # no number needs more than two figures, so the numbers are taken as 0 to 99 (non-negative)

    # circle[k] is the number in the k-th square: circle[0] is A, circle[1] is B, ..., circle[9] is K.
    circle = VarArray(size=n_squares, dom=range(max_number + 1))

    # The given numbers: A=16, B=2, F=8, G=14, keyed by the index of their square.
    placed = {0: 16, 1: 2, 5: 8, 6: 14}

    satisfy(
        # A different number in each square.
        AllDifferent(circle),
        # The four numbers placed as examples stand as they are.
        [circle[k] == number for k, number in placed.items()],
        # For any two adjacent squares p and p + 1, the sum of their squares equals the sum of
        # the squares of the two squares diametrically opposite them, p + half and p + half + 1.
        [
            circle[p] * circle[p] + circle[(p + 1) % n_squares] * circle[(p + 1) % n_squares]
            == circle[(p + half) % n_squares] * circle[(p + half) % n_squares]
            + circle[(p + half + 1) % n_squares] * circle[(p + half + 1) % n_squares]
            for p in range(n_squares)
        ],
    )

    # The keys are the output names. The square E is circle[4]: E is a reserved word for the
    # solver, so the variable is not named E.
    return {
        "A": circle[0],
        "B": circle[1],
        "C": circle[2],
        "D": circle[3],
        "E": circle[4],
        "F": circle[5],
        "G": circle[6],
        "H": circle[7],
        "I": circle[8],
        "K": circle[9],
    }


if __name__ == "__main__":
    outputs = create_model({})
    if solve() is SAT:
        for name, variable in outputs.items():
            print(name, "=", value(variable))
    else:
        print("No solution:", status())
