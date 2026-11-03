# dudeney_numbers: a CPMpy model from DCP Rosetta.
# Download the `dudeney_numbers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/dudeney_numbers.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python dudeney_numbers.py dudeney_numbers.json

import cpmpy as cp


def create_model(instance):
    """A Dudeney number is a positive integer that is a perfect cube such that
    the sum of its digits is equal to the cube root of the number. Find such a
    number that is larger than 1."""
    n = instance["n"]  # the number of digits of the number

    # number_digits[i] is the i-th digit of the number, from the most significant
    number_digits = cp.intvar(0, 9, shape=n, name="number_digits")
    # number is the Dudeney number
    number = cp.intvar(0, 10 ** n - 1, name="number")
    # cube_root is the cube root of the number; at most 9 * n, the largest possible digit sum
    cube_root = cp.intvar(1, 9 * n, name="cube_root")

    model = cp.Model()
    # The number is the cube of cube_root.
    model.add(number == cube_root * cube_root * cube_root)
    # The digits sum to the cube root.
    model.add(cube_root == cp.sum(number_digits))
    # The digits spell out the number.
    model.add(number == cp.sum(number_digits * [10 ** (n - i - 1) for i in range(n)]))
    # The number is larger than 1.
    model.add(number > 1)

    return model, {"number": number}


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
