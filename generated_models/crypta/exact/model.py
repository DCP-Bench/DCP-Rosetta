# crypta: an Exact (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/crypta.html
# Run it (after `pip install exact numpy`) with:
#   python crypta.py

from collections import Counter

from exact import Exact

# The three numbers of the puzzle, one letter per digit, most significant digit first.
FIRST = "BAIJJAJIIAHFCFEBBJEA"    # the first addend
SECOND = "DHFGABCDIDBIFFAGFEJE"   # the second addend
TOTAL = "GJEGACDDHFAFJBFIHEEF"    # the sum


def create_model(instance):
    """Cryptarithmetic puzzle: each letter stands for a different digit from 0 to 9,
    no number starts with a zero, and the first addend plus the second addend gives
    the sum."""
    # The letters of the puzzle.
    letters = sorted(set(FIRST + SECOND + TOTAL))
    # The number of digit places in each number.
    width = len(TOTAL)

    solver = Exact()

    # Exact identifies its variables by name.
    # The first letter of each number cannot stand for zero.
    leading = {FIRST[0], SECOND[0], TOTAL[0]}
    # digit[letter] is the digit the letter stands for: 0 to 9, or 1 to 9 for a leading letter.
    for letter in letters:
        solver.addVariable(letter, 1 if letter in leading else 0, 9)

    # stands[letter][d] is 1 when the letter stands for digit d, and 0 when not.
    stands = {letter: {d: f"{letter}_stands_{d}" for d in range(10)} for letter in letters}
    for letter in letters:
        for d in range(10):
            solver.addVariable(stands[letter][d], 0, 1)

    # Each letter stands for exactly one digit.
    for letter in letters:
        solver.addConstraint([(1, stands[letter][d]) for d in range(10)], True, 1, True, 1)

    # The digit of each letter is the digit it stands for.
    for letter in letters:
        solver.addConstraint([(d, stands[letter][d]) for d in range(1, 10)] + [(-1, letter)], True, 0, True, 0)

    # Different letters stand for different digits.
    for d in range(10):
        solver.addConstraint([(1, stands[letter][d]) for letter in letters], False, 0, True, 1)

    # carry[k] is the carry from column k into column k + 1: 0 or 1.
    carry = [f"carry_{k}" for k in range(width - 1)]
    for name in carry:
        solver.addVariable(name, 0, 1)

    # The addition, column by column from the units up: the two digits of the column and
    # the carry in add up to the digit of the sum and ten times the carry out.
    for k in range(width):
        # net[letter] counts the letter in column k, the sum's letter counted negative.
        net = Counter([FIRST[-1 - k], SECOND[-1 - k]])
        net[TOTAL[-1 - k]] -= 1
        terms = [(count, letter) for letter, count in net.items() if count != 0]
        if k > 0:
            terms.append((1, carry[k - 1]))
        if k < width - 1:
            terms.append((-10, carry[k]))
        solver.addConstraint(terms, True, 0, True, 0)

    return solver, {letter: letter for letter in letters}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
