# crypta: a PyCSP3 model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/crypta.html
# Run it (after `pip install pycsp3`, which also needs Java for its ACE solver) with:
#   python crypta.py

from pycsp3 import *


def create_model(instance):
    """Cryptarithmetic puzzle: all letters are distinct digits from 0 to 9, the first letter
    of each number is not zero, and the first two numbers added together give the third."""
    letters = "ABCDEFGHIJ"                # the ten letters of the puzzle, as in the description
    addend_1 = "BAIJJAJIIAHFCFEBBJEA"     # the first number, one letter per digit, most significant first, as in the description
    addend_2 = "DHFGABCDIDBIFFAGFEJE"     # the second number, one letter per digit, as in the description
    total = "GJEGACDDHFAFJBFIHEEF"        # the sum of the two numbers, one letter per digit, as in the description
    base = 10                             # decimal digits, 0 to 9
    n_columns = len(total)                # the three numbers have one letter per column, all of the same length

    # digit[k] is the digit (0 to 9) given to the letter letters[k].
    digit = VarArray(size=len(letters), dom=range(base))
    # All letters are distinct digits.
    satisfy(AllDifferent(digit))

    # The first letter of each number is not zero.
    satisfy(digit[letters.index(word[0])] != 0 for word in (addend_1, addend_2, total))

    def digit_of(word, column):
        # the digit of the letter in this column, columns counted from the right (column 0)
        return digit[letters.index(word[len(word) - 1 - column])]

    # carry[c] is the carry into column c from the column on its right (0 or 1), column 0 being the rightmost.
    carry = VarArray(size=n_columns + 1, dom={0, 1})
    # No carry comes into the rightmost column, and none goes out of the leftmost, as the sum has no column beyond it.
    satisfy(carry[0] == 0, carry[n_columns] == 0)

    # Each column adds the two digits and the carry in, and gives the digit of the sum and the carry out.
    satisfy(
        digit_of(addend_1, c) + digit_of(addend_2, c) + carry[c] == digit_of(total, c) + base * carry[c + 1]
        for c in range(n_columns)
    )

    # The digit of each letter A to J.
    return {letter: digit[k] for k, letter in enumerate(letters)}


if __name__ == "__main__":
    outputs = create_model({})
    if solve() is SAT:
        for name, variable in outputs.items():
            print(name, "=", value(variable))
    else:
        print("No solution:", status())
