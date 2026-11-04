# pythagorean_triplet: a cvc5 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/pythagorean_triplet.html
# Run it (after `pip install cvc5 numpy`) with:
#   python pythagorean_triplet.py

import cvc5.pythonic as c5


def create_model(instance):
    """Find the Pythagorean triplet a, b, c of natural numbers with a^2 + b^2 = c^2
    whose three members add up to 1000."""
    # a, b and c are the three members of the triplet. Each is at least 1, and the
    # other two are at least 1 too, so each is at most 998.
    a, b, c = c5.Ints("a b c")

    solver = c5.Solver()

    # Each member is a natural number from 1 to 998.
    solver.add(a >= 1, a <= 998, b >= 1, b <= 998, c >= 1, c <= 998)

    # The three members add up to 1000.
    solver.add(a + b + c == 1000)

    # The squares of a and b add up to the square of c.
    solver.add(a * a + b * b == c * c)

    return solver, {"a": a, "b": b, "c": c}


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
