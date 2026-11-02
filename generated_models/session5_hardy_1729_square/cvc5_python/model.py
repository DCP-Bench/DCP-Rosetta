# session5_hardy_1729_square: a cvc5 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_hardy_1729_square.html
# Run it (after `pip install cvc5 numpy`) with:
#   python session5_hardy_1729_square.py

import cvc5.pythonic as c5


def create_model(instance):
    """Find four different numbers between 1 and 100 such that the sum of the squares
    of the first two equals the sum of the squares of the last two: a^2 + b^2 = c^2 + d^2."""
    least, most = 1, 100  # the smallest and the largest number allowed

    # a, b, c, d are the four numbers
    a, b, c, d = c5.Ints("a b c d")
    numbers = [a, b, c, d]

    solver = c5.Solver()

    # Each number is between the smallest and the largest allowed.
    solver.add([c5.And(v >= least, v <= most) for v in numbers])
    # The four numbers are different.
    solver.add(c5.Distinct(numbers))
    # The squares of a and b add up to the squares of c and d.
    solver.add(a * a + b * b == c * c + d * d)

    return solver, {"a": a, "b": b, "c": c, "d": d}


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
