# crypta: a cvc5 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/crypta.html
# Run it (after `pip install cvc5 numpy`) with:
#   python crypta.py

from itertools import combinations

import cvc5.pythonic as c5

# The first addend, the second addend and their sum, as the puzzle writes them.
ADDEND_1 = "BAIJJAJIIAHFCFEBBJEA"
ADDEND_2 = "DHFGABCDIDBIFFAGFEJE"
SUM = "GJEGACDDHFAFJBFIHEEF"
# The letters of the puzzle.
LETTERS = "ABCDEFGHIJ"
# The digits.
DIGITS = range(10)


def create_model(instance):
    """Cryptarithmetic puzzle: each of the letters A to J stands for a different
    digit from 0 to 9, no number starts with a zero, and the addition of the two
    twenty-letter numbers must give the third."""
    # is_digit[c][v] is true when letter c stands for the digit v.
    is_digit = {c: [c5.Bool(f"{c}_{v}") for v in DIGITS] for c in LETTERS}

    solver = c5.Solver()

    # Each letter stands for at least one digit, and not for two digits at once.
    solver.add([c5.Or(is_digit[c]) for c in LETTERS])
    solver.add([c5.Or(c5.Not(is_digit[c][v]), c5.Not(is_digit[c][w]))
                for c in LETTERS for v, w in combinations(DIGITS, 2)])

    # The digit of each letter.
    digit = {c: c5.Sum([c5.If(b, v, 0) for v, b in zip(DIGITS, is_digit[c])])
             for c in LETTERS}

    # Different letters stand for different digits.
    solver.add([c5.Or(c5.Not(is_digit[c][v]), c5.Not(is_digit[e][v]))
                for v in DIGITS for c, e in combinations(LETTERS, 2)])

    # No number starts with a zero.
    solver.add([digit[word[0]] != 0 for word in (ADDEND_1, ADDEND_2, SUM)])

    # carry[k] is the carry from column k into the column to its left. No carry
    # leaves the leftmost column, and none enters the rightmost one.
    n = len(SUM)
    carry = [0] + [c5.Int(f"carry_{k}") for k in range(1, n)] + [0]
    solver.add([c5.And(0 <= c, c <= 1) for c in carry[1:n]])

    # Each column adds up: its two addend digits and the carry from the column on
    # the right give its sum digit and the carry to the left.
    for i in range(n):
        solver.add(
            digit[ADDEND_1[i]] + digit[ADDEND_2[i]] + carry[i + 1]
            == digit[SUM[i]] + 10 * carry[i])

    # The digit of each letter.
    outputs = {c: digit[c] for c in LETTERS}
    return solver, outputs


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
