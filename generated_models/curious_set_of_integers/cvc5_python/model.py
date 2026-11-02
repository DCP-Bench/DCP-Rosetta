# curious_set_of_integers: a cvc5 (Python) model from DCP Rosetta.
# Download the `curious_set_of_integers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/curious_set_of_integers.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python curious_set_of_integers.py curious_set_of_integers.json

import math

import cvc5.pythonic as c5


def create_model(instance):
    """The integers 1, 3, 8 and 120 form a set in which the product of any two
    integers is one less than a perfect square. Find a fifth number (at least 0)
    that can be added to the set without destroying this property."""
    max_val = instance["max_val"]  # the largest value the fifth number may take

    # The integers of the set given in the problem
    given = [1, 3, 8, 120]

    # The fifth number, which is added to the set
    number = c5.Int("number")

    solver = c5.Solver()

    # It is at least 0 and at most max_val.
    solver.add(number >= 0, number <= max_val)

    # The product of the fifth number with each given integer is one less than a
    # perfect square. The roots of these squares are at most top.
    top = math.isqrt(max(given) * max_val + 1)
    solver.add([c5.Or([a * number + 1 == j * j for j in range(top + 1)]) for a in given])

    return solver, {"number": number}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
