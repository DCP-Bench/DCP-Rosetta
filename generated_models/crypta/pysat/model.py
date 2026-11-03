# crypta: a PySAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/crypta.html
# Run it (after `pip install "python-sat[pblib]" numpy`) with:
#   python crypta.py

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine

# The two addends and their sum, letter by letter from the most significant digit.
FIRST = "BAIJJAJIIAHFCFEBBJEA"
SECOND = "DHFGABCDIDBIFFAGFEJE"
TOTAL = "GJEGACDDHFAFJBFIHEEF"


def create_model(instance):
    """Cryptarithmetic puzzle: the letters A to J stand for digits so that the first two
    numbers, added together, give the third."""
    letters = sorted(set(FIRST + SECOND + TOTAL))  # the ten letters A to J
    width = len(TOTAL)  # the addition has one column per digit of the sum

    pool = IDPool()
    # the first letter of each number, which is not zero
    leading = {FIRST[0], SECOND[0], TOTAL[0]}
    # digit[letter] is the digit the letter stands for
    digit = {letter: Integer(letter, 1 if letter in leading else 0, 9, vpool=pool)
             for letter in letters}
    # carry[k] is the carry from column k into column k + 1, 0 or 1
    carry = [Integer(f"carry_{k}", 0, 1, vpool=pool) for k in range(width - 1)]
    engine = IntegerEngine(vars=list(digit.values()) + carry, vpool=pool)

    # every letter stands for a different digit
    engine.add_alldifferent(list(digit.values()))

    # The addition column by column, from the units up: the two addend digits and the
    # carry from the column before make the digit of the sum plus ten times the carry on.
    for k in range(width):
        addends = digit[FIRST[-1 - k]] + digit[SECOND[-1 - k]]
        if k > 0:
            addends = addends + carry[k - 1]
        result = digit[TOTAL[-1 - k]]
        if k < width - 1:
            result = result + 10 * carry[k]
        engine.add_linear(addends == result)

    # the digit of each letter A to J
    return engine.clausify(), {letter: digit[letter] for letter in letters}


if __name__ == "__main__":
    import numpy as np
    from pysat.solvers import Solver

    formula, outputs = create_model({})

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
