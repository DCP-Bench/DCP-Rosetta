# session1_bank_card: a SCIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_bank_card.html
# Run it (after `pip install pyscipopt numpy`) with:
#   python session1_bank_card.py

import numpy as np
from pyscipopt import Model


def create_model(instance):
    """Find a 4 digit PIN abcd, with a, b, c and d its digits, such that no two
    digits are the same, the 2-digit number cd is 3 times the 2-digit number ab,
    and the 2-digit number da is 2 times the 2-digit number bc. The outputs
    a, b, c and d are the digits of the PIN.

    The instance file is empty ([]): the statement fixes all the data, so the
    argument is not read."""

    model = Model("session1_bank_card")

    # pin[i, v] is 1 when position i of the PIN holds the digit v, where
    # position 0 is a, 1 is b, 2 is c and 3 is d. Every digit is 0 to 9. The
    # statement's 4 digit PIN would also bar a = 0; nothing here bars it, and
    # none is needed, because the constraints below admit no solution with a = 0.
    # SCIP has no all-different, so "no two digits are the same" is written
    # with one-hot binaries: every position holds exactly one digit, and every
    # digit is held by at most one position.
    pin = model.addMatrixVar((4, 10), vtype="B", name="pin")
    model.addMatrixCons(pin.sum(axis=1) == 1)  # each position holds one digit
    model.addMatrixCons(pin.sum(axis=0) <= 1)  # no digit is held twice

    # The digits as numbers: pin @ [0, ..., 9] is the digit each position holds.
    a, b, c, d = pin @ np.arange(10)

    # The 2-digit number cd (10 * c + d) is 3 times the 2-digit number ab.
    model.addCons(10 * c + d == 3 * (10 * a + b))

    # The 2-digit number da (10 * d + a) is 2 times the 2-digit number bc.
    model.addCons(10 * d + a == 2 * (10 * b + c))

    # No objective: the statement only asks for a PIN that meets the facts.
    return model, {"a": a, "b": b, "c": c, "d": d}


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
