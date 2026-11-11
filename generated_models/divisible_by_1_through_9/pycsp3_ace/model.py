# divisible_by_1_through_9: a PyCSP3 model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/divisible_by_1_through_9.html
# Run it (after `pip install pycsp3`, which also needs Java for its ACE solver) with:
#   python divisible_by_1_through_9.py

from pycsp3 import *


def create_model(instance):
    """Find a 10 digit number that uses each of the digits 0 to 9 exactly once and where
    the number formed by the first n digits of the number is divisible by n. Read the
    digits from left to right."""
    n_digits = 10

    # lcm of 1 to 10. A number and its remainder on division by 2520 leave the same
    # remainder on division by each of 1 to 10, because each of them divides 2520. The
    # full prefixes (up to 10 digits) would not fit ACE's 32-bit integers, so the
    # remainders are tracked instead.
    modulus = 2520

    # digits[i] is the digit in position i + 1 from the left of the number
    digits = VarArray(size=n_digits, dom=range(10))

    # remainders[i] is the first i + 1 digits of the number, taken modulo 2520
    remainders = VarArray(size=n_digits, dom=range(modulus))

    satisfy(
        # Each of the digits 0 to 9 is used exactly once.
        AllDifferent(digits),
        # A 10 digit number has no leading zero.
        digits[0] != 0,
        # The first digit is the remainder of the one-digit prefix.
        remainders[0] == digits[0],
        # Each further prefix is the previous prefix shifted one place left, plus the next digit.
        (remainders[i] == (10 * remainders[i - 1] + digits[i]) % modulus for i in range(1, n_digits)),
        # The first n digits form a number divisible by n, for n = 2 to 10 (every number is divisible by 1).
        (remainders[i] % (i + 1) == 0 for i in range(1, n_digits)),
    )

    return {"digits": digits}


if __name__ == "__main__":
    outputs = create_model({})
    if solve() is SAT:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())
