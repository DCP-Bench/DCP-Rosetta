# send_more_money: a SCIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/send_more_money.html
# Run it (after `pip install pyscipopt numpy`) with:
#   python send_more_money.py

import numpy as np
from pyscipopt import Model

# The rows of the digit table for the two letters that start a word: S (SEND) and M (MORE, MONEY).
S, M = 0, 4


def create_model(instance):
    """Send More Money: give each letter s, e, n, d, m, o, r, y a different digit
    from 0 to 9 so that SEND + MORE = MONEY when the words are read in base ten,
    with no word starting with 0. The instance file is empty ([]): the puzzle is
    fixed by its statement, so the model reads no data.

    Returns the model and a dict from each letter to its digit."""

    model = Model("send_more_money")

    # digit[l, v] is 1 when letter l stands for the digit v, and 0 when not.
    # Rows are the letters S, E, N, D, M, O, R, Y; columns are the digits 0 to 9.
    digit = model.addMatrixVar((8, 10), vtype="B", name="digit")

    # Each letter stands for exactly one digit.
    model.addMatrixCons(digit.sum(axis=1) == 1)

    # Different letters stand for different digits. SCIP has no all-different
    # constraint, so this says that each digit is taken by at most one letter.
    model.addMatrixCons(digit.sum(axis=0) <= 1)

    # No word starts with 0: SEND starts with S, and MORE and MONEY both start
    # with M, so S and M are not 0.
    model.addCons(digit[S, 0] == 0)
    model.addCons(digit[M, 0] == 0)

    # value[l] is the digit that letter l stands for, a linear expression in digit.
    value = digit @ np.arange(10)
    s, e, n, d, m, o, r, y = value

    # SEND + MORE = MONEY, each word read as its digits in base ten.
    send = 1000 * s + 100 * e + 10 * n + d
    more = 1000 * m + 100 * o + 10 * r + e
    money = 10000 * m + 1000 * o + 100 * n + 10 * e + y
    model.addCons(send + more == money)

    # The digit of each letter; there is no objective, the puzzle asks for any solution.
    return model, {"s": s, "e": e, "n": n, "d": d, "m": m, "o": o, "r": r, "y": y}


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
