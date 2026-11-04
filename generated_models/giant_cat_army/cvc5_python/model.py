# giant_cat_army: a cvc5 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/giant_cat_army.html
# Run it (after `pip install cvc5 numpy`) with:
#   python giant_cat_army.py

import math

import cvc5.pythonic as c5


def create_model(instance):
    """Build a list of 24 distinct whole numbers, each at most 60, that starts with 0 and
    ends with 14. Each step adds 5, adds 7, or takes the square root of a perfect square.
    The list holds 2, then 10, then 14, with other numbers allowed between them."""
    n = 24  # the length of the list
    max_value = 60  # the largest number on the list
    # the largest square root of a number on the list
    root_max = math.isqrt(max_value)

    # x[i] is the i-th number on the list.
    x = [c5.Int(f"x_{i}") for i in range(n)]

    solver = c5.Solver()

    # The list starts with 0 and ends with 14.
    solver.add(x[0] == 0, x[n - 1] == 14)

    # Every number is from 0 to 60.
    solver.add([v >= 0 for v in x] + [v <= max_value for v in x])

    # The numbers are all different.
    solver.add(c5.Distinct(x))

    # Each step adds 5, adds 7, or takes the square root of a perfect square: from k * k
    # back to k.
    for i in range(n - 1):
        solver.add(c5.Or(
            [x[i + 1] == x[i] + 5, x[i + 1] == x[i] + 7]
            + [c5.And(x[i] == k * k, x[i + 1] == k) for k in range(root_max + 1)]))

    # The number 2 comes before the number 10 on the list. The list ends with 14.
    solver.add(c5.Or(
        [c5.And(x[p] == 2, x[q] == 10) for p in range(n) for q in range(p + 1, n)]))

    return solver, {"x": x}


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
