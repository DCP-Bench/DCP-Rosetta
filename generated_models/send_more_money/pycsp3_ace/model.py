# send_more_money: a PyCSP3 model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/send_more_money.html
# Run it (after `pip install pycsp3`, which also needs Java for its ACE solver) with:
#   python send_more_money.py

from pycsp3 import *


def create_model(instance):
    """The Send More Money puzzle: assign a different digit from 0 to 9 to each letter so that
    SEND + MORE = MONEY holds, where the first letter of each word is not zero."""
    base = 10  # the digits are written in base 10

    s = Var(dom=range(base))  # the digit of S, the first letter of SEND
    e = Var(dom=range(base))  # the digit of E
    n = Var(dom=range(base))  # the digit of N
    d = Var(dom=range(base))  # the digit of D
    m = Var(dom=range(base))  # the digit of M, the first letter of MORE
    o = Var(dom=range(base))  # the digit of O
    r = Var(dom=range(base))  # the digit of R
    y = Var(dom=range(base))  # the digit of Y, the last letter of MONEY

    satisfy(
        # Each letter stands for a different digit.
        AllDifferent(s, e, n, d, m, o, r, y),
        # The first letter of each word is not zero.
        s != 0,
        m != 0,
        # SEND + MORE = MONEY, written out in place values.
        base**3 * s + base**2 * e + base * n + d + base**3 * m + base**2 * o + base * r + e
        == base**4 * m + base**3 * o + base**2 * n + base * e + y,
    )

    return {"s": s, "e": e, "n": n, "d": d, "m": m, "o": o, "r": r, "y": y}


if __name__ == "__main__":
    outputs = create_model({})
    if solve() is SAT:
        for name, variable in outputs.items():
            print(name, "=", value(variable))
    else:
        print("No solution:", status())
