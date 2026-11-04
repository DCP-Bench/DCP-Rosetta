# isbn: a cvc5 (Python) model from DCP Rosetta.
# Download the `isbn.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/isbn.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python isbn.py isbn.json

import cvc5.pythonic as c5


def create_model(instance):
    """Fill in the unknown digits of a 13-digit ISBN so that it is valid. The ISBN starts
    with 978 or 979, and its digits, weighted 1 and 3 in turn from the left, sum to a
    multiple of 10."""
    given = instance["isbn_init"]  # the digits of the ISBN, -1 for an unknown digit
    n_digits = len(given)

    # isbn[i]: digit i of the ISBN
    isbn = [c5.Int(f"isbn_{i}") for i in range(n_digits)]

    solver = c5.Solver()

    # Every digit is between 0 and 9.
    for digit in isbn:
        solver.add(digit >= 0, digit <= 9)

    # The known digits keep their value.
    solver.add([digit == g for digit, g in zip(isbn, given) if g != -1])

    # The ISBN starts with 978 or 979.
    solver.add(isbn[0] == 9, isbn[1] == 7, c5.Or(isbn[2] == 8, isbn[2] == 9))

    # The last digit is the check digit: the weighted sum of all 13 digits is a multiple of 10.
    weighted_sum = c5.Sum([digit if i % 2 == 0 else 3 * digit for i, digit in enumerate(isbn)])
    solver.add(weighted_sum % 10 == 0)

    return solver, {"isbn": isbn}


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
