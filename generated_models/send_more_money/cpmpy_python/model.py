# send_more_money: a CPMpy model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/send_more_money.html
# Run it (after `pip install cpmpy`) with:
#   python send_more_money.py

import cpmpy as cp


def create_model(instance):
    """Cryptarithmetic puzzle: give each letter a different digit so that
    SEND + MORE = MONEY holds, with no leading zero in any word."""
    # The puzzle has no instance data: the words are the problem statement.

    # The digit (0 to 9) that each letter stands for
    s, e, n, d, m, o, r, y = cp.intvar(0, 9, shape=8, name=["s", "e", "n", "d", "m", "o", "r", "y"])

    model = cp.Model()

    # Different letters take different digits.
    model.add(cp.AllDifferent([s, e, n, d, m, o, r, y]))

    # The first letter of a word cannot be zero.
    model.add(s > 0)
    model.add(m > 0)

    # SEND + MORE = MONEY, each word read as a decimal number.
    send = 1000 * s + 100 * e + 10 * n + d
    more = 1000 * m + 100 * o + 10 * r + e
    money = 10000 * m + 1000 * o + 100 * n + 10 * e + y
    model.add(send + more == money)

    return model, {"s": s, "e": e, "n": n, "d": d, "m": m, "o": o, "r": r, "y": y}


if __name__ == "__main__":
    model, outputs = create_model({})
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
