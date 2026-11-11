# isbn: a PyCSP3 model from DCP Rosetta.
# Download the `isbn.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/isbn.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python isbn.py isbn.json

from pycsp3 import *


def create_model(instance):
    """An ISBN-13 is a 13-digit number whose last digit is a check digit, calculated from the first 12
    digits: multiply them alternately by 1 and 3, starting with 1, and sum the products; the check digit
    is (10 - (sum % 10)) % 10. Given an ISBN-13 where -1 stands for an unknown digit, find the unknown
    digits so that the number is a valid ISBN-13, which must start with 978 or 979."""
    isbn_init = instance["isbn_init"]  # isbn_init[i] is digit i of the given ISBN, or -1 when that digit is unknown
    n_digits = len(isbn_init)
    unknown = -1  # the value in isbn_init that marks an unknown digit
    base = 10  # decimal digits, 0 to 9

    # isbn[i] is digit i of the ISBN, counted from the front
    isbn = VarArray(size=n_digits, dom=range(base))

    # weights[i] is the weight of digit i in the check sum: 1 for the first digit, 3 for the second, alternately
    weights = [1 if i % 2 == 0 else 3 for i in range(n_digits)]

    satisfy(
        # Each given digit is kept; the digits given as -1 are unknown and free.
        [isbn[i] == digit for i, digit in enumerate(isbn_init) if digit != unknown],
        # The ISBN starts with 978 or 979: its first two digits are 9 and 7.
        isbn[0] == 9,
        isbn[1] == 7,
        # Its third digit is 8 (978) or 9 (979).
        isbn[2] in {8, 9},
        # The weighted digit sum, the check digit included, is a multiple of 10: the last digit is then (10 - (sum of the first 12 weighted digits) % 10) % 10, as stated.
        Sum(weights[i] * isbn[i] for i in range(n_digits)) % base == 0,
    )

    return {"isbn": isbn}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())
