# isbn: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `isbn.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/isbn.html
# Then run it on the first instance (after `pip install ortools`):
#   python isbn.py isbn.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Fill in the unknown digits of a 13-digit ISBN so that it is valid. It starts with
    978 or 979, and its last digit is the check digit: the first 12 digits are weighted
    alternately by 1 and 3, summed, and the check digit is (10 - (sum % 10)) % 10."""
    given = instance["isbn_init"]  # the digits of the ISBN that are known, -1 for an unknown digit
    n_digits = len(given)

    model = cp_model.CpModel()

    # isbn[i]: digit i of the ISBN. It starts with 978 or 979.
    isbn = [model.new_int_var(9, 9, "isbn_0"), model.new_int_var(7, 7, "isbn_1"),
            model.new_int_var(8, 9, "isbn_2")]
    isbn += [model.new_int_var(0, 9, f"isbn_{i}") for i in range(3, n_digits)]

    # The known digits keep their value.
    for i in range(n_digits):
        if given[i] != -1:
            model.add(isbn[i] == given[i])

    # The weighted sum of the first 12 digits, weights 1 and 3 alternating from the left.
    weighted_sum = sum(isbn[i] * (1 if i % 2 == 0 else 3) for i in range(n_digits - 1))
    # remainder: the weighted sum modulo 10
    remainder = model.new_int_var(0, 9, "remainder")
    model.add_modulo_equality(remainder, weighted_sum, 10)
    # complement: 10 - remainder, between 1 and 10
    complement = model.new_int_var(1, 10, "complement")
    model.add(complement == 10 - remainder)
    # The last digit is the complement modulo 10, so a remainder of 0 gives a check digit of 0.
    model.add_modulo_equality(isbn[n_digits - 1], complement, 10)

    return model, {"isbn": isbn}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
