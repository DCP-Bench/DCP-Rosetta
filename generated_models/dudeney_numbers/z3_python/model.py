# dudeney_numbers: a Z3 (Python) model from DCP Rosetta.
# Download the `dudeney_numbers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/dudeney_numbers.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python dudeney_numbers.py dudeney_numbers.json

import z3


def create_model(instance):
    """A Dudeney number is a positive integer that is a perfect cube such that the
    sum of its digits is equal to the cube root of the number. Find such a number
    that is larger than 1 and has at most n digits."""
    n = instance["n"]  # the most digits the number may have

    # number_digits[i] is the i-th digit of the number, most significant first, with
    # zeros on the left to make n digits
    number_digits = [z3.Int(f"number_digits_{i}") for i in range(n)]
    # number is the Dudeney number
    number = z3.Int("number")
    # cube_root is the cube root of the number; a digit sum is at most 9 per digit
    cube_root = z3.Int("cube_root")

    # The conditions that the number has to meet.
    solver = z3.Solver()

    # Each digit is between 0 and 9.
    solver.add([z3.And(d >= 0, d <= 9) for d in number_digits])

    # The number has at most n digits, and its cube root is between 1 and 9 * n.
    solver.add(z3.And(number >= 0, number <= 10**n - 1))
    solver.add(z3.And(cube_root >= 1, cube_root <= 9 * n))

    # The number is the cube of its cube root.
    solver.add(number == cube_root * cube_root * cube_root)

    # The digits sum to the cube root.
    solver.add(cube_root == z3.Sum(number_digits))

    # The digits spell out the number.
    solver.add(number == z3.Sum([number_digits[i] * 10 ** (n - i - 1) for i in range(n)]))

    # The number is larger than 1.
    solver.add(number > 1)

    return solver, {"number": number}


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
