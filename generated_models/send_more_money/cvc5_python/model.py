# send_more_money: a cvc5 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/send_more_money.html
# Run it (after `pip install cvc5 numpy`) with:
#   python send_more_money.py

import cvc5.pythonic as c5


def create_model(instance):
    """Cryptarithmetic puzzle: give each letter a different digit so that
    SEND + MORE = MONEY holds, with no leading zero in SEND or MORE."""
    # The digit (0 to 9) that each letter stands for
    s, e, n, d, m, o, r, y = c5.Ints("s e n d m o r y")

    # All eight letters
    letters = [s, e, n, d, m, o, r, y]

    solver = c5.Solver()

    # Each letter stands for a digit from 0 to 9.
    for v in letters:
        solver.add(v >= 0, v <= 9)

    # Different letters take different digits.
    solver.add(c5.Distinct(letters))

    # The first letter of SEND and of MORE is not zero.
    solver.add(s != 0, m != 0)

    # SEND, MORE and MONEY, each read as a decimal number
    send = 1000 * s + 100 * e + 10 * n + d
    more = 1000 * m + 100 * o + 10 * r + e
    money = 10000 * m + 1000 * o + 100 * n + 10 * e + y

    # SEND + MORE is MONEY.
    solver.add(send + more == money)

    return solver, {"s": s, "e": e, "n": n, "d": d, "m": m, "o": o, "r": r, "y": y}


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
