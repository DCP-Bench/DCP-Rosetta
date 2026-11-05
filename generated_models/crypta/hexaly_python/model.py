"""Crypta: a cryptarithm with two 20-digit numbers and their sum, each letter a different digit and no number
starting with a zero."""
import hexaly.optimizer as hx

FIRST = "BAIJJAJIIAHFCFEBBJEA"
SECOND = "DHFGABCDIDBIFFAGFEJE"
TOTAL = "GJEGACDDHFAFJBFIHEEF"
LETTERS = "ABCDEFGHIJ"


def build(instance):
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # is_digit[l][d] = 1 if letter l stands for digit d. Booleans with linear sums let Hexaly treat the
    # different-digits rule and the column sums as one linear system, which it can also prove things about.
    is_digit = {letter: [model.bool() for _ in range(10)] for letter in LETTERS}
    # Every letter is one digit, and different letters are different digits: each digit is used once
    for letter in LETTERS:
        model.constraint(model.sum(is_digit[letter]) == 1)
    for d in range(10):
        model.constraint(model.sum(is_digit[letter][d] for letter in LETTERS) == 1)
    # No number starts with a zero
    for word in (FIRST, SECOND, TOTAL):
        model.constraint(is_digit[word[0]][0] == 0)
    # The digit each letter stands for
    digit = {letter: model.sum(d * is_digit[letter][d] for d in range(10)) for letter in LETTERS}

    # The numbers have 20 digits, more than a 64-bit integer holds, so add them column by column as on paper:
    # carry[k] is what the column k places from the right passes to the next one (0 or 1)
    columns = len(TOTAL)
    carry = [model.int(0, 1) for _ in range(columns)]
    for k in range(columns):
        carried_in = carry[k - 1] if k else 0
        # The two digits in this column plus the carry make the digit of the sum here, and a carry
        model.constraint(digit[FIRST[-1 - k]] + digit[SECOND[-1 - k]] + carried_in == digit[TOTAL[-1 - k]] + 10 * carry[k])
    # Nothing is carried beyond the leading column of the sum
    model.constraint(carry[columns - 1] == 0)

    return optimizer, digit
