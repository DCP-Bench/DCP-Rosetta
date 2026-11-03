"""General store: replace each letter by a different digit so that the sixteen words add up to ALL WOOL."""
import hexaly.optimizer as hx

WORDS = ["CHESS", "CASH", "BOWWOW", "CHOPS", "ALSOPS", "PALEALE", "COOL", "BASS", "HOPS", "ALES", "HOES",
         "APPLES", "COWS", "CHEESE", "CHSOAP", "SHEEP"]
TOTAL = "ALLWOOL"
LETTERS = "CHESABOWPL"


def build(instance):
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # Each letter is a digit, and different letters are different digits
    digit = {letter: model.int(0, 9) for letter in LETTERS}
    for a in range(len(LETTERS)):
        for b in range(a + 1, len(LETTERS)):
            model.constraint(digit[LETTERS[a]] != digit[LETTERS[b]])
    # No number starts with a zero
    for letter in {word[0] for word in WORDS + [TOTAL]}:
        model.constraint(digit[letter] >= 1)

    def value(word):
        return model.sum(10 ** k * digit[letter] for k, letter in enumerate(reversed(word)))

    # The words above the line add up to ALL WOOL
    model.constraint(model.sum(value(word) for word in WORDS) == value(TOTAL))

    return optimizer, {letter: digit[letter] for letter in LETTERS}
