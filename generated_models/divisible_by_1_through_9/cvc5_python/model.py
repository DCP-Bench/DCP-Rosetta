# Divisible by 1 through 9: a 10-digit number that uses each digit 0 to 9 exactly once,
# where the number formed by its first n digits is divisible by n, for n = 1 to 10.
# Output "digits" is the ten digits of the number, read from left to right.
import cvc5.pythonic as cz


def build(instance):
    # The description fixes the digit count (10) and the digit set, so the instance
    # carries no data this model needs.
    # digits[i] is the digit at position i, read from left to right.
    digits = cz.Ints(" ".join(f"d{i}" for i in range(10)))
    cons = []

    # Each digit is one of 0 to 9.
    for x in digits:
        cons.append(x >= 0)
        cons.append(x <= 9)

    # Each of the digits 0 to 9 is used exactly once.
    cons.append(cz.Distinct(list(digits)))

    # The number has 10 digits, so the leading digit is not zero.
    cons.append(digits[0] >= 1)

    # The number formed by the first n digits is divisible by n, for n = 1 to 10.
    # A prefix with n digits is written as prefix_n = n * q_n with q_n a free integer.
    for n in range(1, 11):
        prefix = cz.Sum([digits[i] * 10 ** (n - 1 - i) for i in range(n)])
        q = cz.Int(f"q{n}")
        cons.append(q >= 0)
        cons.append(prefix == n * q)

    return cons, {"digits": list(digits)}
