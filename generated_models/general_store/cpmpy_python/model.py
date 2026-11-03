# general_store: a CPMpy model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/general_store.html
# Run it (after `pip install cpmpy`) with:
#   python general_store.py

import cpmpy as cp

# The sixteen words above the line, which add up to the total below it.
WORDS = ["CHESS", "CASH", "BOWWOW", "CHOPS", "ALSOPS", "PALEALE", "COOL", "BASS",
         "HOPS", "ALES", "HOES", "APPLES", "COWS", "CHEESE", "CHSOAP", "SHEEP"]
TOTAL = "ALLWOOL"


def create_model(instance):
    """The owner of a general store has put up a sign: sixteen words that add up to
    'ALL WOOL'. Each different letter stands for a different digit; find the digit
    of every letter. The sign fixes all the data, so the instance is not used."""
    # x[k] is the digit that the k-th letter stands for; digit[c] looks it up by letter
    letters = "CHESABOWPL"
    x = cp.intvar(0, 9, shape=len(letters), name="x")
    digit = dict(zip(letters, x))

    def value(word):
        # The number a word spells: its last letter counts for 1, the one before for 10, and so on.
        return cp.sum([10 ** k * digit[c] for k, c in enumerate(reversed(word))])

    model = cp.Model()
    # Different letters stand for different digits.
    model.add(cp.AllDifferent(x))
    # The sixteen words add up to the total.
    model.add(cp.sum([value(word) for word in WORDS]) == value(TOTAL))

    return model, digit


if __name__ == "__main__":
    model, outputs = create_model({})
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
