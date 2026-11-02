# pythagorean_triplet: a Z3 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/pythagorean_triplet.html
# Run it (after `pip install z3-solver numpy`) with:
#   python pythagorean_triplet.py

import z3


def create_model(instance):
    """Find three natural numbers a, b, c with a^2 + b^2 = c^2 whose sum is 1000.
    Exactly one such triplet exists."""
    total = 1000          # the sum of the three numbers
    largest = total // 2  # no number reaches half the sum, so each is below 500

    # a, b and c are the three numbers of the triplet
    a, b, c = z3.Ints("a b c")

    solver = z3.Solver()

    solver.add(
        # Natural numbers, each at most 500.
        *[z3.And(v >= 1, v <= largest) for v in (a, b, c)],
        # The three numbers add up to 1000.
        a + b + c == total,
        # a and b are the legs and c the hypotenuse of a right triangle.
        a * a + b * b == c * c,
    )
    return solver, {"a": a, "b": b, "c": c}


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
