# pythagorean_triplet: a PyCSP3 model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/pythagorean_triplet.html
# Run it (after `pip install pycsp3`, which also needs Java for its ACE solver) with:
#   python pythagorean_triplet.py

from pycsp3 import *


def create_model(instance):
    """A Pythagorean triplet is a set of three natural numbers a, b and c for which
    a^2 + b^2 = c^2. The order of a and b does not matter. Find the triplet for which
    a + b + c = 1000."""
    total = 1000

    # a is the first number of the triplet, a natural number taken as 1 or more.
    # Each number is below total, since the other two are at least 1.
    a = Var(dom=range(1, total))
    # b is the second number of the triplet, a natural number taken as 1 or more.
    b = Var(dom=range(1, total))
    # c is the number whose square is a^2 + b^2, a natural number taken as 1 or more.
    c = Var(dom=range(1, total))

    satisfy(
        # The three numbers add up to total.
        a + b + c == total,
        # a^2 + b^2 = c^2.
        a * a + b * b == c * c,
        # The order of a and b does not matter, so a is taken below b (a = b is impossible: 2a^2 = c^2 has no integer solution).
        a < b,
    )

    return {"a": a, "b": b, "c": c}


if __name__ == "__main__":
    outputs = create_model({})
    if solve() is SAT:
        for name, variable in outputs.items():
            print(name, "=", value(variable))
    else:
        print("No solution:", status())
