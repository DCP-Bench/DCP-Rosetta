# isbn: an Exact (Python) model from DCP Rosetta.
# Download the `isbn.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/isbn.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python isbn.py isbn.json

from exact import Exact


def create_model(instance):
    """Fill in the unknown digits of a 13-digit ISBN so that it is valid: it starts with
    978 or 979, and its last digit is the check digit of the first twelve."""
    isbn_init = instance["isbn_init"]  # the digits of the ISBN, -1 for a digit that is unknown
    n_digits = len(isbn_init)          # the number of digits in the ISBN, 13

    solver = Exact()

    # Exact identifies its variables by name.
    # isbn[i] is digit i of the ISBN. The ISBN starts with 9, 7 and then 8 or 9; every
    # other digit is 0 to 9. A given digit is fixed to its value.
    isbn = [f"isbn_{i}" for i in range(n_digits)]
    prefix_bounds = {0: (9, 9), 1: (7, 7), 2: (8, 9)}
    for i, name in enumerate(isbn):
        low, high = prefix_bounds.get(i, (0, 9))
        if isbn_init[i] != -1:
            low, high = max(low, isbn_init[i]), min(high, isbn_init[i])
        solver.addVariable(name, low, high)

    # weights[i] is the weight of digit i in the check sum: 1 for even i, 3 for odd i.
    weights = [1 if i % 2 == 0 else 3 for i in range(n_digits - 1)]

    # tens is the check sum, the twelve weighted digits plus the check digit, divided by 10.
    max_total = 9 * sum(weights) + 9
    solver.addVariable("tens", 0, max_total // 10)

    # The check digit makes the weighted sum of the first twelve digits, plus the check
    # digit itself, a multiple of 10.
    solver.addConstraint(list(zip(weights, isbn[:-1])) + [(1, isbn[-1]), (-10, "tens")],
                         True, 0, True, 0)

    return solver, {"isbn": isbn}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
