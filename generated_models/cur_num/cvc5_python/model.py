# cur_num: a cvc5 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cur_num.html
# Run it (after `pip install cvc5 numpy`) with:
#   python cur_num.py

import math

import cvc5.pythonic as c5


def create_model(instance):
    """The number 48 is peculiar: adding 1 to it gives a square number, and adding 1
    to its half gives a square number too. Find another number between 1 and 10000
    with this peculiarity."""
    # The number to find
    peculiar = c5.Int("peculiar")

    solver = c5.Solver()

    # It lies between 1 and 10000 and is not the example 48.
    solver.add(peculiar >= 1, peculiar <= 10000, peculiar != 48)

    # Adding 1 gives a square number k * k, with k at most the square root of 10001.
    solver.add(
        c5.Or([peculiar + 1 == k * k for k in range(1, math.isqrt(10001) + 1)])
    )

    # Half of the number, plus 1, is a square number m * m. So the number is even and
    # equals 2 * (m * m - 1), with m at most the square root of 5001.
    solver.add(
        c5.Or([peculiar == 2 * (m * m - 1) for m in range(1, math.isqrt(5001) + 1)])
    )

    return solver, {"peculiar": peculiar}


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
