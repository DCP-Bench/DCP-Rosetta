# circling_squares: a cvc5 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/circling_squares.html
# Run it (after `pip install cvc5 numpy`) with:
#   python circling_squares.py

import cvc5.pythonic as c5


def create_model(instance):
    """Circling the squares: place a different number in each of ten squares of a circle, so that
    the sum of the squares of any two adjacent numbers equals the sum of the squares of the two
    numbers diametrically opposite them."""
    names = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "K"]  # the squares in order around the circle
    n = len(names)
    given = {"A": 16, "B": 2, "F": 8, "G": 14}  # the four numbers the puzzle places
    # the whole numbers a square can hold: fractions are not allowed, and no number needs more than two figures
    values = list(range(0, 100))

    # x[i] is the number in the square named names[i]
    x = [c5.Int(f"x_{i}") for i in range(n)]
    # sq[i] is the square of the number in that square
    sq = [c5.Int(f"sq_{i}") for i in range(n)]

    solver = c5.Solver()

    # Each square holds one of the allowed numbers, and its square is the square of that number.
    solver.add([c5.Or([c5.And(xi == v, si == v * v) for v in values]) for xi, si in zip(x, sq)])

    # Each square holds a different number.
    solver.add(c5.Distinct(x))

    # The four numbers given in the puzzle stand as they are.
    solver.add([x[names.index(name)] == value for name, value in given.items()])

    # Two adjacent squares have the same sum of squares as the two squares opposite them.
    solver.add([sq[i] + sq[(i + 1) % n] == sq[(i + 5) % n] + sq[(i + 6) % n] for i in range(n)])

    outputs = {name: xi for name, xi in zip(names, x)}
    return solver, outputs


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
