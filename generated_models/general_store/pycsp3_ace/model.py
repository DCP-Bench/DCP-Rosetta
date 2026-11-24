# general_store: a PyCSP3 model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/general_store.html
# Run it (after `pip install pycsp3`, which also needs Java for its ACE solver) with:
#   python general_store.py

from pycsp3 import *


def create_model(instance):
    """A cryptarithm: each different letter stands for a different digit. The sixteen words
    CHESS, CASH, BOWWOW, ... SHEEP are added and their sum is ALL WOOL. Leading zeros are
    allowed, so a word may start with the digit 0."""
    base = 10  # the digits are the digits of base 10, 0 to base - 1

    # the digit that the letter A stands for
    digit_A = Var(dom=range(base))
    # the digit that the letter B stands for
    digit_B = Var(dom=range(base))
    # the digit that the letter C stands for
    digit_C = Var(dom=range(base))
    # the digit that the letter E stands for (named digit_E since E is a reserved identifier in ACE)
    digit_E = Var(dom=range(base))
    # the digit that the letter H stands for
    digit_H = Var(dom=range(base))
    # the digit that the letter L stands for
    digit_L = Var(dom=range(base))
    # the digit that the letter O stands for
    digit_O = Var(dom=range(base))
    # the digit that the letter P stands for
    digit_P = Var(dom=range(base))
    # the digit that the letter S stands for
    digit_S = Var(dom=range(base))
    # the digit that the letter W stands for
    digit_W = Var(dom=range(base))

    # digit[ch] is the digit variable of the letter ch; the dict keys are the output names
    digit = {
        "A": digit_A, "B": digit_B, "C": digit_C, "E": digit_E, "H": digit_H,
        "L": digit_L, "O": digit_O, "P": digit_P, "S": digit_S, "W": digit_W,
    }

    def word_value(word):
        """The number a word spells: its letters read as digits in base, leftmost letter the most significant."""
        return Sum(digit[ch] * base ** (len(word) - 1 - i) for i, ch in enumerate(word))

    # The words above the line of the sum, in the order of the puzzle.
    addends = [
        "CHESS", "CASH", "BOWWOW", "CHOPS", "ALSOPS", "PALEALE", "COOL", "BASS",
        "HOPS", "ALES", "HOES", "APPLES", "COWS", "CHEESE", "CHSOAP", "SHEEP",
    ]

    satisfy(
        # Each different letter stands for a different digit.
        AllDifferent(list(digit.values())),
        # The words above the line add up to ALL WOOL.
        Sum(word_value(word) for word in addends) == word_value("ALLWOOL"),
    )

    return digit


if __name__ == "__main__":
    outputs = create_model({})
    if solve() is SAT:
        for name, variable in outputs.items():
            print(name, "=", value(variable))
    else:
        print("No solution:", status())
