from hermax.model import Model

# The sixteen addends of the sum, from the problem description, one per line
# of the sign, and the total they must add up to.
WORDS = [
    "CHESS", "CASH", "BOWWOW", "CHOPS", "ALSOPS", "PALEALE", "COOL", "BASS",
    "HOPS", "ALES", "HOES", "APPLES", "COWS", "CHEESE", "CHSOAP", "SHEEP",
]
TOTAL = "ALLWOOL"


def build(instance):
    letters = sorted(set("".join(WORDS) + TOTAL))

    m = Model()
    digits = m.int_vector("digit", len(letters), 0, 9)
    x = {c: digits[k] for k, c in enumerate(letters)}

    # Each different letter stands for a different digit.
    m &= digits.all_different()

    # Column-wise addition: the digits in each column, plus the carry from the
    # column to its right, equal the total's digit plus ten times the carry to
    # the left. The total has no digit beyond its width, so the last carry is 0.
    width = max(len(w) for w in WORDS + [TOTAL])
    carry = [0] + [m.int(f"carry_{c}", 0, 16) for c in range(1, width)] + [0]
    for c in range(width):
        column = sum(x[w[-1 - c]] for w in WORDS if len(w) > c)
        total_digit = x[TOTAL[-1 - c]]
        m &= (column + carry[c] == total_digit + 10 * carry[c + 1])

    outputs = {c: x[c] for c in "ABCEHLOPSW"}
    return m, outputs
