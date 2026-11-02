# dudeney_numbers: a PuLP (Python) model from DCP Rosetta.
# Download the `dudeney_numbers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/dudeney_numbers.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python dudeney_numbers.py dudeney_numbers.json

import pulp


def create_model(instance):
    """A Dudeney number is a positive integer that is a perfect cube such that
    the sum of its digits is equal to the cube root of the number. Find such a
    number of at most n digits that is larger than 1."""
    n_digits = instance["n"]  # the maximum number of digits of the number
    max_root = 9 * n_digits   # the cube root is at most 9 * n, the largest possible digit sum

    problem = pulp.LpProblem("dudeney_numbers", pulp.LpMinimize)

    # digits[i] is the i-th digit of the number, from the most significant; a leading zero is allowed, so the number may have fewer digits
    digits = [pulp.LpVariable(f"digit_{i}", 0, 9, cat="Integer") for i in range(n_digits)]
    # number is the Dudeney number, from 2 up to the largest n-digit number
    number = pulp.LpVariable("number", 2, 10**n_digits - 1, cat="Integer")

    # root[r] is 1 when the cube root of the number is r
    root = {r: pulp.LpVariable(f"root_{r}", cat="Binary") for r in range(1, max_root + 1)}
    # Exactly one cube root is chosen.
    problem += pulp.lpSum(root.values()) == 1

    # The number is the cube of its cube root.
    problem += number == pulp.lpSum(r**3 * var for r, var in root.items())

    # The cube root is the sum of the digits.
    problem += pulp.lpSum(r * var for r, var in root.items()) == pulp.lpSum(digits)

    # The digits spell out the number.
    problem += number == pulp.lpSum(digits[i] * 10 ** (n_digits - i - 1) for i in range(n_digits))

    # There is no objective: any number that meets the rules is an answer.
    return problem, {"number": number}


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
