# isbn: a PuLP (Python) model from DCP Rosetta.
# Download the `isbn.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/isbn.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python isbn.py isbn.json

import pulp


def create_model(instance):
    """Fill in the unknown digits of a 13-digit ISBN so that it is valid. It starts with
    978 or 979, and its last digit is the check digit: the first 12 digits are weighted
    alternately by 1 and 3, and the check digit is 10 minus the last digit of their sum,
    with 10 written as 0."""
    isbn_init = instance["isbn_init"]  # isbn_init[i]: digit i of the ISBN, or -1 when it is unknown
    n_digits = len(isbn_init)

    problem = pulp.LpProblem("isbn", pulp.LpMinimize)

    # isbn[i] is digit i of the ISBN. An ISBN-13 starts with 978 or 979.
    isbn = [
        pulp.LpVariable("isbn_0", 9, 9, cat="Integer"),
        pulp.LpVariable("isbn_1", 7, 7, cat="Integer"),
        pulp.LpVariable("isbn_2", 8, 9, cat="Integer"),
    ]
    isbn += [pulp.LpVariable(f"isbn_{i}", 0, 9, cat="Integer") for i in range(3, n_digits)]

    # The known digits keep their value.
    for i, known in enumerate(isbn_init):
        if known != -1:
            problem += isbn[i] == known

    # The weighted sum of the first 12 digits, with weights 1 and 3 alternating from the left.
    weighted = pulp.lpSum((1 if i % 2 == 0 else 3) * isbn[i] for i in range(n_digits - 1))
    # No weighted sum can exceed 9 * 3 for each of the 12 digits.
    largest_sum = 9 * 3 * (n_digits - 1)

    # quotient is how many tens the weighted sum holds, and remainder is what is left over.
    quotient = pulp.LpVariable("quotient", 0, largest_sum // 10, cat="Integer")
    remainder = pulp.LpVariable("remainder", 0, 9, cat="Integer")
    problem += weighted == 10 * quotient + remainder

    # remainder_is_zero is 1 when the remainder is 0, and 0 otherwise.
    remainder_is_zero = pulp.LpVariable("remainder_is_zero", cat="Binary")
    problem += remainder <= 9 * (1 - remainder_is_zero)
    problem += remainder >= 1 - remainder_is_zero

    # The check digit is 10 minus the remainder, and 0 when the remainder is 0, since 10 is not a digit.
    problem += isbn[n_digits - 1] == 10 - remainder - 10 * remainder_is_zero

    return problem, {"isbn": isbn}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
