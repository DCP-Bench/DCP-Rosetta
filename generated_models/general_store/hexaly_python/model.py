"""General store: replace each letter by a different digit so that the sixteen words add up to ALL WOOL."""
import hexaly.optimizer as hx

WORDS = ["CHESS", "CASH", "BOWWOW", "CHOPS", "ALSOPS", "PALEALE", "COOL", "BASS", "HOPS", "ALES", "HOES",
         "APPLES", "COWS", "CHEESE", "CHSOAP", "SHEEP"]
TOTAL = "ALLWOOL"
LETTERS = "CHESABOWPL"


def build(instance):
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # is[l][d] = 1 if letter l stands for digit d. Booleans with linear sums let Hexaly treat the different-digits
    # rule and the column sums as one linear system, which it handles far better than digits compared pairwise.
    is_digit = {letter: [model.bool() for _ in range(10)] for letter in LETTERS}
    # Every letter is one digit, and different letters are different digits: each digit is used once. The statement
    # does not forbid a leading zero, and the only assignment that makes the sum work has one.
    for letter in LETTERS:
        model.constraint(model.sum(is_digit[letter]) == 1)
    for d in range(10):
        model.constraint(model.sum(is_digit[letter][d] for letter in LETTERS) == 1)
    # The digit each letter stands for
    digit = {letter: model.sum(d * is_digit[letter][d] for d in range(10)) for letter in LETTERS}

    # Add the words column by column, as on paper: carry[k] is what the column k places from the right
    # passes to the next one
    columns = len(TOTAL)
    carry = [model.int(0, len(WORDS)) for _ in range(columns)]
    for k in range(columns):
        in_column = [digit[word[-1 - k]] for word in WORDS if k < len(word)]
        carried_in = carry[k - 1] if k else 0
        # The digits of the words in this column plus the carry make the digit of ALL WOOL here, and a carry
        model.constraint(model.sum(in_column) + carried_in == digit[TOTAL[-1 - k]] + 10 * carry[k])
    # Nothing is carried beyond the leading column of ALL WOOL
    model.constraint(carry[columns - 1] == 0)

    return optimizer, digit
