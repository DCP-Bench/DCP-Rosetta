# isbn: a CPMpy model from DCP Rosetta.
# Download the `isbn.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/isbn.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python isbn.py isbn.json

import cpmpy as cp
import numpy as np


def create_model(instance):
    """Fill in the unknown digits of a 13-digit ISBN so that it is valid: it starts with
    978 or 979, and the last digit is the check digit (10 - (sum % 10)) % 10, where the
    sum weights the first 12 digits alternately by 1 and 3."""
    given = instance["isbn_init"]  # given[i]: digit i of the ISBN, or -1 when it is unknown
    n = len(given)

    # isbn[i] is digit i of the ISBN
    isbn = cp.intvar(0, 9, shape=n, name="isbn")

    model = cp.Model()

    # The known digits keep their value.
    for i in range(n):
        if given[i] != -1:
            model.add(isbn[i] == given[i])

    # An ISBN-13 starts with 978 or 979.
    model.add(isbn[0] == 9)
    model.add(isbn[1] == 7)
    model.add((isbn[2] == 8) | (isbn[2] == 9))

    # The last digit is the check digit of the first 12 digits,
    # which are weighted alternately by 1 and 3, starting with 1.
    weights = np.array([1 if i % 2 == 0 else 3 for i in range(n - 1)])
    model.add(isbn[n - 1] == (10 - (cp.sum(isbn[:n - 1] * weights) % 10)) % 10)

    return model, {"isbn": isbn}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
