# Divisible by 1 through 9: find a ten-digit number that uses each digit 0 to 9 exactly
# once and where, for every n, the number formed by its first n digits is divisible by n.
# PyCSP3 star-imports its vocabulary, as every PyCSP3 model does.
# ruff: noqa: F403, F405
from pycsp3 import *

# The statement fixes all the data (ten digits, divisors 1 to 10), so the instance has
# no fields.
n_digits = 10

# digits[i]: the digit at position i of the number, read from left to right
digits = VarArray(size=n_digits, dom=range(10))

satisfy(
    # Each of the digits 0 to 9 is used exactly once.
    AllDifferent(digits),

    # The number formed by the first n digits is divisible by n.
    # That number is the sum of digits[j] * 10**(n-1-j), which for n = 10 is above
    # 2**31 - 1, the largest integer ACE holds. Replacing each place value
    # 10**(n-1-j) by its remainder modulo n leaves the remainder of the sum modulo n
    # unchanged and keeps the sum below 1000.
    [Sum((10 ** (n - 1 - j) % n) * digits[j] for j in range(n)) % n == 0
     for n in range(1, n_digits + 1)],
)
