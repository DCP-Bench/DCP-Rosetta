# divisible_by_1_through_9: a CPMpy model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/divisible_by_1_through_9.html
# Run it (after `pip install cpmpy`) with:
#   python divisible_by_1_through_9.py

import cpmpy as cp


def create_model(instance):
    """Find a 10 digit number that uses each of the digits 0 to 9 exactly once and
    where the number formed by the first n digits is divisible by n."""
    n_digits = 10

    # digits[i] is the i-th digit of the number, read from left to right
    digits = cp.intvar(0, 9, shape=n_digits, name="digits")
    # prefix[i] is the number formed by the first i + 1 digits
    prefix = cp.intvar(0, 10 ** n_digits, shape=n_digits, name="prefix")
    # number is the whole ten digit number
    number = prefix[n_digits - 1]

    model = cp.Model()
    # Each digit from 0 to 9 is used exactly once.
    model.add(cp.AllDifferent(digits))
    for i in range(n_digits):
        # prefix[i] is made of the first i + 1 digits, the leftmost digit being the most significant.
        model.add(prefix[i] == cp.sum(digits[:i + 1] * [10 ** (i - j) for j in range(i + 1)]))
        # The number formed by the first i + 1 digits is divisible by i + 1.
        model.add(prefix[i] % (i + 1) == 0)

    return model, {"number": number}


if __name__ == "__main__":
    model, outputs = create_model({})
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
