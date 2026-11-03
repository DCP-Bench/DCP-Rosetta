# general_store: a hermax (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/general_store.html
# Run it (after `pip install hermax`) with:
#   python general_store.py

from hermax.model import Model, sum_expr

# The sixteen words above the line of the sign, and the total they add up to.
WORDS = ["CHESS", "CASH", "BOWWOW", "CHOPS", "ALSOPS", "PALEALE", "COOL", "BASS",
         "HOPS", "ALES", "HOES", "APPLES", "COWS", "CHEESE", "CHSOAP", "SHEEP"]
TOTAL = "ALLWOOL"


def create_model(instance):
    """General store puzzle: give each letter of the sign a different digit so that the
    sixteen words add up to ALL WOOL. It is a satisfaction problem with no objective."""
    # The instance carries no data: the words and the total are fixed by the statement.

    m = Model()

    # The ten different letters of the sign.
    letters = sorted(set("".join(WORDS) + TOTAL))
    # digit[letter] is the digit that the letter stands for
    digit = {letter: m.int(letter, 0, 9) for letter in letters}

    # Each different letter stands for a different digit.
    m &= m.vector([digit[letter] for letter in letters]).all_different()

    def value(word):
        # The number a word spells: its letters' digits weighted by their place value.
        return sum(10 ** (len(word) - 1 - p) * digit[ch] for p, ch in enumerate(word))

    # The sixteen words, added together, make ALL WOOL.
    m &= (sum_expr(value(word) for word in WORDS) == value(TOTAL))

    return m, {letter: digit[letter] for letter in letters}


if __name__ == "__main__":
    model, outputs = create_model({})
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
