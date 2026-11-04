# crypta: a hermax (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/crypta.html
# Run it (after `pip install hermax`) with:
#   python crypta.py
from hermax.model import Model

# The cryptarithm is fixed by the problem statement; the instance file carries no data.
# Words are written least significant letter last, as they are read.
FIRST = "BAIJJAJIIAHFCFEBBJEA"    # first addend
SECOND = "DHFGABCDIDBIFFAGFEJE"  # second addend
TOTAL = "GJEGACDDHFAFJBFIHEEF"   # the sum


def create_model(instance):
    """Cryptarithmetic puzzle: assign a different digit 0..9 to each letter so that
    FIRST + SECOND = TOTAL holds as an ordinary addition. No number starts with a zero."""
    # every distinct letter of the puzzle gets one digit
    letters = sorted(set(FIRST + SECOND + TOTAL))
    width = len(TOTAL)  # all three words have the same length

    m = Model()

    # digit[letter] is the digit that the letter stands for, 0..9
    digit = {letter: m.int(letter, 0, 9) for letter in letters}

    # Different letters stand for different digits.
    m &= m.vector([digit[letter] for letter in letters]).all_different()

    # The first letter of each number is not zero.
    for word in (FIRST, SECOND, TOTAL):
        m &= (digit[word[0]] != 0)

    # The addition is done column by column, from the units column up.
    # carry[k] is the carry from column k into column k + 1, either 0 or 1.
    carry = [m.int(f"carry_{k}", 0, 1) for k in range(width - 1)]
    for k in range(width):
        # Column k: the two addend digits plus the carry from column k - 1
        # equal the total's digit plus ten times the carry into column k + 1.
        left = digit[FIRST[-1 - k]] + digit[SECOND[-1 - k]]
        if k > 0:
            left = left + carry[k - 1]
        right = digit[TOTAL[-1 - k]]
        if k < width - 1:
            right = right + 10 * carry[k]
        m &= (left == right)

    # No objective: any assignment that satisfies the addition is a solution.
    # The outputs are the digit of each letter, A to J.
    return m, {letter: digit[letter] for letter in letters}


if __name__ == "__main__":
    model, outputs = create_model({})
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
