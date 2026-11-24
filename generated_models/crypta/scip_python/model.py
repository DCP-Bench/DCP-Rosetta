# crypta: a SCIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/crypta.html
# Run it (after `pip install pyscipopt numpy`) with:
#   python crypta.py

import numpy as np
from pyscipopt import Model

# The three words of the puzzle, most significant letter first, as the statement
# writes them, and the letters of the puzzle.
FIRST = "BAIJJAJIIAHFCFEBBJEA"
SECOND = "DHFGABCDIDBIFFAGFEJE"
TOTAL = "GJEGACDDHFAFJBFIHEEF"
LETTERS = "ABCDEFGHIJ"


def create_model(instance):
    """Cryptarithm: give each letter A to J a different digit from 0 to 9 so that
    the sum FIRST + SECOND = TOTAL holds, for the three words given above.
    The first letter of each of the three numbers is not zero. The words are fixed
    by the statement, so the function reads nothing from `instance`. It is a satisfaction problem with no objective; the
    outputs are the digit of each letter."""
    model = Model("crypta")
    n = len(TOTAL)  # the number of columns of the sum
    index = {letter: i for i, letter in enumerate(LETTERS)}

    # x[l, d] is 1 when letter l (0 for A up to 9 for J) stands for digit d.
    # SCIP has no all-different constraint, so the ten letters take ten different
    # digits as a permutation matrix: each letter has one digit, and each digit
    # has one letter.
    x = model.addMatrixVar((10, 10), vtype="B", name="x")
    model.addMatrixCons(x.sum(axis=1) == 1)  # each letter takes exactly one digit
    model.addMatrixCons(x.sum(axis=0) == 1)  # each digit is taken by exactly one letter

    # value[l] is the digit of letter l: the sum of d * x[l, d] over the digits d.
    # It is an expression, not a new variable, since x already holds it.
    value = x @ np.arange(10)

    # The first letter of each number cannot be zero.
    for word in (FIRST, SECOND, TOTAL):
        model.addCons(value[index[word[0]]] >= 1)

    # carry[j] is 1 when column j - 1 passes a carry on to column j, with columns
    # counted from the right, the units column being 0. Nothing is carried into the
    # units column (carry[0] = 0), and nothing leaves the leftmost column (carry[n] = 0)
    # because a carry out of it would need a 21st digit, which TOTAL does not have.
    # A column adds at most 9 + 9 + 1 = 19, so a carry is 0 or 1.
    carry = [0] + [model.addVar(f"carry_{j}", vtype="B") for j in range(1, n)] + [0]

    # Column by column from the right, the digits of FIRST and SECOND in the column
    # plus the carry in equal the digit of TOTAL plus 10 times the carry out. Working
    # column by column keeps every coefficient at most 10; a weighted sum over the whole
    # numbers would need coefficients up to 10**19, beyond what floating-point arithmetic
    # keeps exact.
    for j in range(n):
        a, b, s = (word[-1 - j] for word in (FIRST, SECOND, TOTAL))
        model.addCons(
            value[index[a]] + value[index[b]] + carry[j]
            == value[index[s]] + 10 * carry[j + 1]
        )

    outputs = {letter: value[index[letter]] for letter in LETTERS}
    return model, outputs


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
