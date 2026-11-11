# session5_hardy_1729_square: a PyCSP3 model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_hardy_1729_square.html
# Run it (after `pip install pycsp3`, which also needs Java for its ACE solver) with:
#   python session5_hardy_1729_square.py

from pycsp3 import *


def create_model(instance):
    """Find four different numbers between 1 and 100 such that the sum of the squares
    of the first two equals the sum of the squares of the other two:
    a^2 + b^2 = c^2 + d^2."""
    max_number = 100  # the numbers lie between 1 and this bound, as the statement says

    # a is the first of the four numbers
    a = Var(dom=range(1, max_number + 1))
    # b is the second of the four numbers
    b = Var(dom=range(1, max_number + 1))
    # c is the third of the four numbers
    c = Var(dom=range(1, max_number + 1))
    # d is the fourth of the four numbers
    d = Var(dom=range(1, max_number + 1))

    satisfy(
        # The four numbers are all different.
        AllDifferent([a, b, c, d]),
        # The squares of a and b add up to the squares of c and d.
        a * a + b * b == c * c + d * d,
    )

    return {"a": a, "b": b, "c": c, "d": d}


if __name__ == "__main__":
    outputs = create_model({})
    if solve() is SAT:
        for name, variable in outputs.items():
            print(name, "=", value(variable))
    else:
        print("No solution:", status())
