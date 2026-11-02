"""Send more money: SEND + MORE = MONEY with a different digit for each letter and no word starting with zero."""
import hexaly.optimizer as hx

LETTERS = "semndory"


def build(instance):
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    digit = {letter: model.int(0, 9) for letter in LETTERS}
    # Each letter stands for a different digit
    for a in range(len(LETTERS)):
        for b in range(a + 1, len(LETTERS)):
            model.constraint(digit[LETTERS[a]] != digit[LETTERS[b]])
    # The first letter of a word cannot be zero
    model.constraint(digit["s"] >= 1)
    model.constraint(digit["m"] >= 1)

    def value(word):
        return model.sum(10 ** k * digit[letter] for k, letter in enumerate(reversed(word)))

    # SEND + MORE = MONEY
    model.constraint(value("send") + value("more") == value("money"))

    return optimizer, digit
