# circling_squares: a SCIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/circling_squares.html
# Run it (after `pip install pyscipopt numpy`) with:
#   python circling_squares.py

import numpy as np
from pyscipopt import Model


def create_model(instance):
    """Circling the squares: place a different whole number in each of ten squares
    on a circle, labelled A, B, C, D, E, F, G, H, I, K in order around the circle.
    For any two adjacent squares, the sum of the squares of their two numbers must
    equal the sum of the squares of the two numbers in the diametrically opposite
    squares. The statement fixes A = 16, B = 2, F = 8 and G = 14 and asks for the
    other six numbers. The instance file is empty ([]), so the instance argument is
    not read. Returns the model and the ten numbers, keyed by square letter.
    """
    model = Model("circling_squares")

    # Ten squares, in order around the circle: position 0 is A and position 9 is K.
    # The count of ten comes from the statement.
    squares = 10
    # The numbers are the whole numbers 0 to 99. Both bounds are assumptions, not derived:
    # the statement says no number need contain more than two figures (the upper bound
    # 99), and it never mentions negative numbers, so 0 as the lower bound is our choice.
    values = np.arange(100)

    # place[s, v] is 1 when square s holds the number v, and 0 otherwise.
    # SCIP has no all-different constraint and addCons has no !=, so the distinct
    # numbers are written as a one-hot table: every square holds exactly one number,
    # and every number sits on at most one square.
    place = model.addMatrixVar((squares, len(values)), vtype="B", name="place")

    # Each square holds exactly one number.
    model.addMatrixCons(place.sum(axis=1) == 1)
    # Each number is on at most one square, so the ten numbers are all different.
    model.addMatrixCons(place.sum(axis=0) <= 1)

    # number[s] is the number on square s, and squared[s] is its square.
    number = place @ values
    squared = place @ (values ** 2)

    # The statement fixes four numbers: A (position 0) is 16, B (position 1) is 2,
    # F (position 5) is 8 and G (position 6) is 14. These are data of the problem.
    for s, v in {0: 16, 1: 2, 5: 8, 6: 14}.items():
        model.addCons(place[s, v] == 1)

    # The circle's rule: for adjacent squares i and i+1 (mod 10), the sum of their squares
    # equals the sum of the squares of the opposite adjacent squares i+5 and i+6 (mod 10).
    # The equation for i+5 is the same equation as the one for i, so i = 0 to 4 covers
    # all ten adjacent pairs.
    for i in range(5):
        model.addCons(
            squared[i] + squared[(i + 1) % squares]
            == squared[(i + 5) % squares] + squared[(i + 6) % squares]
        )

    # No objective: the puzzle asks for any arrangement that meets the rule, so this is
    # a satisfaction problem.

    # One output per square letter, in order around the circle.
    outputs = {letter: number[s] for s, letter in enumerate("ABCDEFGHIK")}
    return model, outputs


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
