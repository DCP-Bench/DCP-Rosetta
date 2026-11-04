# isbn: a PySAT (Python) model from DCP Rosetta.
# Download the `isbn.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/isbn.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python isbn.py isbn.json

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Fill in the unknown digits of a 13-digit ISBN so that it is valid. It starts with
    978 or 979, and its last digit is the check digit: the first 12 digits are weighted
    alternately by 1 and 3 and summed, and the check digit is (10 - (sum % 10)) % 10."""
    isbn_init = instance["isbn_init"]  # the digits of the ISBN, -1 for each unknown digit
    n_digits = len(isbn_init)          # 13 digits; the last one is the check digit

    pool = IDPool()

    # isbn[i]: digit i of the ISBN
    isbn = [Integer(f"isbn{i}", 0, 9, vpool=pool) for i in range(n_digits)]

    # weights[i]: the weight of digit i in the check sum, 1 and 3 alternating from the left
    weights = [1 if i % 2 == 0 else 3 for i in range(n_digits - 1)]

    # multiple: the check sum, with the check digit added, divided by 10. The first 12 digits
    # add up to at most 9 * sum(weights) and the check digit to at most 9, so this bound holds.
    multiple = Integer("multiple", 0, (9 * sum(weights) + 9) // 10, vpool=pool)

    engine = IntegerEngine(vars=isbn + [multiple], vpool=pool)

    # Each known digit keeps its value.
    for i in range(n_digits):
        if isbn_init[i] != -1:
            engine.add_linear(isbn[i] == isbn_init[i])

    # The ISBN starts with 978 or 979.
    engine.add_linear(isbn[0] == 9)
    engine.add_linear(isbn[1] == 7)
    engine.add_linear(isbn[2] >= 8)

    # The check sum of the first 12 digits, plus the check digit, is a multiple of 10. The
    # check digit is between 0 and 9, so it is the one digit that makes the total a multiple of 10.
    check_sum = sum(weights[i] * isbn[i] for i in range(n_digits - 1))
    engine.add_linear(check_sum + isbn[n_digits - 1] == 10 * multiple)

    return engine.clausify(), {"isbn": isbn}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.solvers import Solver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
