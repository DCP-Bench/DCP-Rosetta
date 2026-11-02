# dudeney_numbers: a cvc5 (Python) model from DCP Rosetta.
# Download the `dudeney_numbers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/dudeney_numbers.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python dudeney_numbers.py dudeney_numbers.json

import cvc5.pythonic as c5


def create_model(instance):
    """A Dudeney number is a positive integer that is a perfect cube such that
    the sum of its digits is equal to the cube root of the number. Find such a
    number that is larger than 1."""
    n = instance["n"]  # the number of digits of the number

    # top is the largest root whose cube has at most n digits
    top = 1
    while (top + 1) ** 3 < 10 ** n:
        top += 1

    # digits[i] is the digit worth 10 ** i in the number
    digits = [c5.Int(f"digit_{i}") for i in range(n)]
    # the Dudeney number
    number = c5.Int("number")
    # the cube root of the number
    root = c5.Int("root")

    # the rules the number, its digits and its root must meet
    solver = c5.Solver()

    # Each digit is one of 0 to 9.
    for d in digits:
        solver.add(d >= 0)
        solver.add(d <= 9)

    # The number is written with these digits.
    solver.add(number == c5.Sum([d * 10 ** i for i, d in enumerate(digits)]))

    # The number is larger than 1.
    solver.add(number > 1)

    # The digits add up to the cube root.
    solver.add(c5.Sum(digits) == root)

    # The number is the cube of root, for a root from 2 to top.
    # cube_options holds one such choice of root for each value from 2 to top.
    cube_options = [c5.And(root == c, number == c ** 3) for c in range(2, top + 1)]
    if len(cube_options) == 1:
        solver.add(cube_options[0])
    else:
        solver.add(c5.Or(cube_options))

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
