# isbn: a Z3 (Python) model from DCP Rosetta.
# Download the `isbn.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/isbn.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python isbn.py isbn.json

import z3


def create_model(instance):
    """Fill in the unknown digits of an ISBN-13 so that it is valid: it starts with 978 or
    979, and its last digit is the check digit of the 12 digits before it."""
    given = instance["isbn_init"]  # given[i]: digit i of the ISBN, or -1 when that digit is unknown
    n_digits = len(given)

    # isbn[i] is digit i of the ISBN
    isbn = [z3.Int(f"isbn_{i}") for i in range(n_digits)]
    solver = z3.Solver()

    solver.add([d >= 0 for d in isbn] + [d <= 9 for d in isbn])

    # The known digits keep their value.
    solver.add([isbn[i] == given[i] for i in range(n_digits) if given[i] != -1])

    # An ISBN-13 starts with 978 or 979.
    solver.add(isbn[0] == 9, isbn[1] == 7, z3.Or(isbn[2] == 8, isbn[2] == 9))

    # The first 12 digits, weighted alternately by 1 and 3 from the left, summed.
    weighted_sum = z3.Sum([isbn[i] * (1 if i % 2 == 0 else 3) for i in range(n_digits - 1)])

    # The last digit is the check digit: (10 - (sum % 10)) % 10.
    solver.add(isbn[n_digits - 1] == (10 - (weighted_sum % 10)) % 10)

    return solver, {"isbn": isbn}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
