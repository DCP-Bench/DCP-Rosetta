# session1_bank_card: a PyCSP3 model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_bank_card.html
# Run it (after `pip install pycsp3`, which also needs Java for its ACE solver) with:
#   python session1_bank_card.py

from pycsp3 import *


def create_model(instance):
    """A 4 digit PIN abcd, where no two digits are the same, the 2-digit number cd is 3 times
    the 2-digit number ab, and the 2-digit number da is 2 times the 2-digit number bc."""
    base = 10  # the digits are written in base 10

    # The digits of the PIN abcd. Each is taken from 0 to 9: the statement does not exclude a zero digit.
    a = Var(dom=range(base))  # the first digit of the PIN
    b = Var(dom=range(base))  # the second digit of the PIN
    c = Var(dom=range(base))  # the third digit of the PIN
    d = Var(dom=range(base))  # the fourth digit of the PIN

    satisfy(
        # No two digits are the same.
        AllDifferent(a, b, c, d),
        # The 2-digit number cd is 3 times the 2-digit number ab.
        base * c + d == 3 * (base * a + b),
        # The 2-digit number da is 2 times the 2-digit number bc.
        base * d + a == 2 * (base * b + c),
    )

    return {"a": a, "b": b, "c": c, "d": d}


if __name__ == "__main__":
    outputs = create_model({})
    if solve() is SAT:
        for name, variable in outputs.items():
            print(name, "=", value(variable))
    else:
        print("No solution:", status())
