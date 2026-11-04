# divisible_by_1_through_9: a Z3 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/divisible_by_1_through_9.html
# Run it (after `pip install z3-solver numpy`) with:
#   python divisible_by_1_through_9.py

import z3


def create_model(instance):
    """Find a ten-digit number that uses each digit 0 to 9 exactly once, such that the
    number formed by its first n digits is divisible by n, for n = 1 to 10."""
    # The puzzle states its own length, so the instance holds no data.
    n = 10

    # Bit-vector encoding: Z3's integer divisibility reasoning is slow on ten nested
    # remainders, while bit-blasted remainders go to the SAT core.
    # A ten-digit number is below 10**10 < 2**34, so 34 bits hold every prefix.
    width = 34

    # digits[i] is the digit at position i, read from left to right (4 bits hold 0..9).
    digits = [z3.BitVec(f"digits_{i}", 4) for i in range(n)]
    # prefix[i] is the number formed by the first i + 1 digits.
    prefix = [z3.BitVec(f"prefix_{i}", width) for i in range(n)]

    solver = z3.Solver()

    # Each digit is at most 9 (the bit-vector is unsigned, so there is no lower bound).
    for d in digits:
        solver.add(z3.ULE(d, 9))

    # Every digit from 0 to 9 is used exactly once.
    solver.add(z3.Distinct(digits))

    # The first digit alone is the first prefix; each further digit extends the
    # previous prefix by one decimal place.
    solver.add(prefix[0] == z3.ZeroExt(width - 4, digits[0]))
    for i in range(1, n):
        solver.add(prefix[i] == 10 * prefix[i - 1] + z3.ZeroExt(width - 4, digits[i]))

    # The first i + 1 digits form a number divisible by its length i + 1.
    for i in range(n):
        solver.add(z3.URem(prefix[i], z3.BitVecVal(i + 1, width)) == 0)

    # The digits go out as integers, since outputs must be Int- or Bool-sorted.
    return solver, {"digits": [z3.BV2Int(d) for d in digits]}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
