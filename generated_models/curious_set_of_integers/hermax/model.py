# curious_set_of_integers: a hermax (Python) model from DCP Rosetta.
# Download the `curious_set_of_integers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/curious_set_of_integers.html
# Then run it on the first instance (after `pip install hermax`):
#   python curious_set_of_integers.py curious_set_of_integers.json

from math import isqrt

from hermax.model import Model

# The problem's given set (problem constants, fixed by the statement): the integers
# 1, 3, 8 and 120 form a set in which the product of any two members is one less than
# a perfect square. The fifth number x must keep that property with each of them.
GIVEN = [1, 3, 8, 120]


def create_model(instance):
    """Find a fifth number x >= 0 such that the product of x with each of the given
    integers 1, 3, 8, 120 is one less than a perfect square, that is a * x + 1 is a
    perfect square for every given a. The search stops at max_val."""
    max_val = instance["max_val"]  # max_val: the largest value the number may take
    # The instance field n (5, the size of the completed set) is not read: the four given
    # members are fixed by the statement, as GIVEN above.

    m = Model()

    # number is the fifth number of the set, between 0 and max_val
    number = m.int("number", 0, max_val)

    # For each given a, x must make a * x + 1 a perfect square. That relation is
    # awkward as arithmetic (it asks whether a number is a square), so we list the
    # values of x in 0..max_val that satisfy it, and post them as a table.
    for a in GIVEN:
        allowed = [(x,) for x in range(max_val + 1)
                   if isqrt(a * x + 1) ** 2 == a * x + 1]
        # a * number + 1 is a perfect square
        m &= m.table([number], allowed=allowed)

    # No objective: any number that keeps the property is an answer.
    return m, {"number": number}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
