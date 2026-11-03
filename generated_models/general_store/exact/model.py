# general_store: an Exact (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/general_store.html
# Run it (after `pip install exact numpy`) with:
#   python general_store.py

from collections import Counter

from exact import Exact


def create_model(instance):
    """The owner of a general store has put up a sign: sixteen words that add up to
    'ALL WOOL'. Each different letter stands for a different digit; find the digit
    of every letter."""
    # The sixteen words above the line, and the total below it.
    words = ["CHESS", "CASH", "BOWWOW", "CHOPS", "ALSOPS", "PALEALE", "COOL", "BASS",
             "HOPS", "ALES", "HOES", "APPLES", "COWS", "CHEESE", "CHSOAP", "SHEEP"]
    total = "ALLWOOL"
    width = len(total)  # the number of columns in the addition

    # The distinct letters on the sign.
    letters = sorted(set("".join(words) + total))

    solver = Exact()

    # Exact identifies its variables by name.
    # Each letter is a digit from 0 to 9.
    for letter in letters:
        solver.addVariable(letter, 0, 9)

    # digit_is[letter][d] is 1 when the letter stands for digit d, and 0 when not.
    digit_is = {letter: {d: f"{letter}_is_{d}" for d in range(10)} for letter in letters}
    for letter in letters:
        for d in range(10):
            solver.addVariable(digit_is[letter][d], 0, 1)
        # Each letter stands for exactly one digit.
        solver.addConstraint([(1, digit_is[letter][d]) for d in range(10)], True, 1, True, 1)
        # The letter takes the value of the digit it stands for.
        solver.addConstraint([(d, digit_is[letter][d]) for d in range(1, 10)] + [(-1, letter)],
                             True, 0, True, 0)

    # Different letters stand for different digits: each digit is used by at most one letter.
    for d in range(10):
        solver.addConstraint([(1, digit_is[letter][d]) for letter in letters], False, 0, True, 1)

    # carry[k] is what column k carries to the column on its left, with columns numbered
    # from the units, 0. A column of sixteen digits carries at most len(words) - 1.
    max_carry = len(words) - 1
    carry = [f"carry_{k}" for k in range(width - 1)]
    for name in carry:
        solver.addVariable(name, 0, max_carry)

    # The addition, column by column from the units: the digits of the words in a column,
    # plus the carry from the column on its right, equal the digit of the total plus ten
    # times the carry to the column on its left.
    for k in range(width):
        # How many times each letter is added in column k, with the total's letter subtracted.
        net = Counter(word[-1 - k] for word in words if len(word) > k)
        net[total[-1 - k]] -= 1
        terms = [(count, letter) for letter, count in net.items() if count != 0]
        if k > 0:
            terms.append((1, carry[k - 1]))
        if k < width - 1:
            terms.append((-10, carry[k]))
        solver.addConstraint(terms, True, 0, True, 0)

    # The digit of each letter.
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
