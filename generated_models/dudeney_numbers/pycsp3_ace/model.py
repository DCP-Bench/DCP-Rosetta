# dudeney_numbers: a PyCSP3 model from DCP Rosetta.
# Download the `dudeney_numbers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/dudeney_numbers.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python dudeney_numbers.py dudeney_numbers.json

from pycsp3 import *


def create_model(instance):
    """A Dudeney Number is a positive integer that is a perfect cube such that the sum of
    its digits is equal to the cube root of the number. Find such a number that is also
    larger than 1 and has at most n digits."""
    n_digits = instance["n"]  # the most digits the number may have

    # The digit sum of a number with at most n digits is at most 9 * n, so the cube root
    # (equal to the digit sum) is at most 9 * n. The cube root is at least 2, so that the
    # number is larger than 1.
    max_root = 9 * n_digits
    min_root = 2

    # root is the cube root of the number, which is also its digit sum
    root = Var(dom=range(min_root, max_root + 1))

    # digits[i] is the digit in place 10 ** i of the number; a leading zero is allowed,
    # so the number has at most n_digits digits. For up to 9 digits the place values stay
    # within ACE's 32-bit integers (ACE rejects larger constants).
    digits = VarArray(size=n_digits, dom=range(10))

    # number is the cube of root, below 10 ** n_digits
    number = Var(dom=range(min_root ** 3, 10 ** n_digits))

    satisfy(
        # The digit sum of the number equals its cube root.
        Sum(digits) == root,
        # The digits are the decimal digits of the number.
        number == Sum(digits[i] * 10 ** i for i in range(n_digits)),
        # The number is a perfect cube of its cube root.
        number == root * root * root,
    )

    return {"number": number}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        for name, variable in outputs.items():
            print(name, "=", value(variable))
    else:
        print("No solution:", status())
