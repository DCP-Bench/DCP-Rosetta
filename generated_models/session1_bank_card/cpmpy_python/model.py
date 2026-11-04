# session1_bank_card: a CPMpy model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_bank_card.html
# Run it (after `pip install cpmpy`) with:
#   python session1_bank_card.py

import cpmpy as cp


def create_model(instance):
    """A bank card has a four-digit PIN abcd: no two digits are the same, the
    two-digit number cd is 3 times ab, and da is 2 times bc."""
    # The puzzle has no instance data: the clues are the problem statement.

    # The four digits of the PIN, a b c d
    a, b, c, d = cp.intvar(0, 9, shape=4, name=["a", "b", "c", "d"])

    model = cp.Model()

    # No two digits are the same.
    model.add(cp.AllDifferent([a, b, c, d]))

    # The two-digit number cd is 3 times the two-digit number ab.
    model.add(10 * c + d == 3 * (10 * a + b))

    # The two-digit number da is 2 times the two-digit number bc.
    model.add(10 * d + a == 2 * (10 * b + c))

    return model, {"a": a, "b": b, "c": c, "d": d}


if __name__ == "__main__":
    model, outputs = create_model({})
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
