# crypta: a Z3 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/crypta.html
# Run it (after `pip install z3-solver numpy`) with:
#   python crypta.py

import z3


def create_model(instance):
    """Cryptarithmetic puzzle: each of the letters A to J stands for a different digit
    from 0 to 9, no number starts with a zero, and the addition of the two twenty-letter
    numbers must give the third."""
    letters = "ABCDEFGHIJ"

    # The three numbers of the sum, most significant letter first.
    first = "BAIJJAJIIAHFCFEBBJEA"
    second = "DHFGABCDIDBIFFAGFEJE"
    result = "GJEGACDDHFAFJBFIHEEF"

    # digit[ch] is the digit that letter ch stands for.
    digit = {ch: z3.BitVec(ch, 4) for ch in letters}

    # carry[k] is true when column k, counted from the right, receives a carry from column k - 1.
    width = len(result)
    carry = [z3.Bool(f"carry_{k}") for k in range(width + 1)]

    # A digit widened so that a column sum of up to 19 fits.
    def wide(d):
        return z3.ZeroExt(1, d)

    solver = z3.Solver()

    # Each letter stands for a digit from 0 to 9, and different letters stand for different digits.
    solver.add([z3.ULE(digit[ch], 9) for ch in letters])
    solver.add(z3.Distinct([digit[ch] for ch in letters]))

    # The first letter of each number is not zero.
    solver.add([digit[word[0]] != 0 for word in (first, second, result)])

    # No carry comes into the rightmost column, and none goes beyond the leftmost column of the result.
    solver.add(z3.Not(carry[0]), z3.Not(carry[width]))

    # Column by column from the right, the two addends and the carry in add up to the digit
    # of the result plus ten times the carry out.
    for k in range(width):
        d1 = digit[first[width - 1 - k]]
        d2 = digit[second[width - 1 - k]]
        dr = digit[result[width - 1 - k]]
        column_sum = wide(d1) + wide(d2) + z3.If(carry[k], z3.BitVecVal(1, 5), z3.BitVecVal(0, 5))
        written = wide(dr) + z3.If(carry[k + 1], z3.BitVecVal(10, 5), z3.BitVecVal(0, 5))
        solver.add(column_sum == written)

    # The digit of each letter, A to J.
    outputs = {ch: z3.BV2Int(digit[ch]) for ch in letters}
    return solver, outputs


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
