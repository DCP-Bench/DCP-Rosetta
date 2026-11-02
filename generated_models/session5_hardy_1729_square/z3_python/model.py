# session5_hardy_1729_square: a Z3 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_hardy_1729_square.html
# Run it (after `pip install z3-solver numpy`) with:
#   python session5_hardy_1729_square.py

import z3


def create_model(instance):
    """Find four different numbers between 1 and 100 such that the sum of the squares
    of the first two equals the sum of the squares of the last two: a^2 + b^2 = c^2 + d^2."""
    # a, b, c and d are the four numbers
    numbers = z3.Ints("a b c d")
    a, b, c, d = numbers

    solver = z3.Solver()

    # The conditions the four numbers must meet.
    # Each number lies between 1 and 100.
    solver.add([z3.And(v >= 1, v <= 100) for v in numbers])
    # The squares of a and b add up to the squares of c and d.
    solver.add(a * a + b * b == c * c + d * d)
    # The four numbers are different.
    solver.add(z3.Distinct(numbers))

    return solver, {"a": a, "b": b, "c": c, "d": d}


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
