# send_more_money: a Z3 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/send_more_money.html
# Run it (after `pip install z3-solver numpy`) with:
#   python send_more_money.py

import z3


def create_model(instance):
    """Cryptarithmetic puzzle: give each letter a different digit so that
    SEND + MORE = MONEY holds, with no leading zero in any word."""
    # The puzzle has no instance data: the words are the problem statement.

    # The digit that each letter stands for
    s, e, n, d, m, o, r, y = letters = [z3.Int(name) for name in "sendmory"]

    solver = z3.Solver()

    # Each letter is a digit from 0 to 9.
    solver.add([z3.And(0 <= letter, letter <= 9) for letter in letters])

    # Different letters take different digits.
    solver.add(z3.Distinct(letters))

    # The first letter of a word cannot be zero.
    solver.add(s > 0, m > 0)

    # SEND, MORE and MONEY, each read as a decimal number, and SEND + MORE = MONEY.
    send = 1000 * s + 100 * e + 10 * n + d
    more = 1000 * m + 100 * o + 10 * r + e
    money = 10000 * m + 1000 * o + 100 * n + 10 * e + y
    solver.add(send + more == money)

    return solver, {"s": s, "e": e, "n": n, "d": d, "m": m, "o": o, "r": r, "y": y}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
