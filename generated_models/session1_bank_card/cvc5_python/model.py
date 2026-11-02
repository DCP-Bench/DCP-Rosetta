# session1_bank_card: a cvc5 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_bank_card.html
# Run it (after `pip install cvc5 numpy`) with:
#   python session1_bank_card.py

import cvc5.pythonic as c5


def create_model(instance):
    """A bank card has a four-digit PIN abcd: no two digits are the same, the
    two-digit number cd is 3 times ab, and da is 2 times bc."""
    # The four digits of the PIN, a b c d
    a, b, c, d = c5.Ints("a b c d")

    # The four digits
    digits = [a, b, c, d]

    solver = c5.Solver()

    # Each digit is from 0 to 9.
    for x in digits:
        solver.add(x >= 0, x <= 9)

    # The PIN and the two-digit numbers ab, bc and da have no leading zero.
    solver.add(a >= 1, b >= 1, d >= 1)

    # No two digits are the same.
    solver.add(c5.Distinct(digits))

    # The two-digit number cd is 3 times the two-digit number ab.
    solver.add(10 * c + d == 3 * (10 * a + b))

    # The two-digit number da is 2 times the two-digit number bc.
    solver.add(10 * d + a == 2 * (10 * b + c))

    return solver, {"a": a, "b": b, "c": c, "d": d}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
