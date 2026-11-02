# Divisible by 1 through 9: find a ten-digit number using each digit 0-9 exactly
# once such that the number formed by its first n digits is divisible by n, for
# n = 1 to 10.
import z3


def build(instance):
    del instance  # the puzzle states its own length

    n = 10  # number of digits

    # Bit-vector encoding: Z3's integer divisibility reasoning is slow on ten
    # nested remainders, while bit-blasted remainders go to the SAT core.
    # A ten-digit number is below 10**10 < 2**34, so 34 bits hold every prefix.
    width = 34

    # digits[i] = the digit at position i, read from left to right (4 bits: 0..9).
    digits = [z3.BitVec(f"digits_{i}", 4) for i in range(n)]
    # prefix[i] = the number formed by the first i + 1 digits.
    prefix = [z3.BitVec(f"prefix_{i}", width) for i in range(n)]

    solver = z3.Solver()

    for d in digits:
        solver.add(z3.ULE(d, 9))

    # Every digit from 0 to 9 is used exactly once.
    solver.add(z3.Distinct(digits))

    # The first digit alone is the first prefix; each further digit extends the
    # previous prefix by one decimal place.
    solver.add(prefix[0] == z3.ZeroExt(width - 4, digits[0]))
    for i in range(1, n):
        solver.add(prefix[i] == 10 * prefix[i - 1] + z3.ZeroExt(width - 4, digits[i]))

    # The first i+1 digits form a number divisible by its length i+1.
    for i in range(n):
        solver.add(z3.URem(prefix[i], z3.BitVecVal(i + 1, width)) == 0)

    # The digits go out as integers: the runner reads Int-sorted expressions only.
    return solver, {"digits": [z3.BV2Int(d) for d in digits]}
