# session1_bank_card: a Z3 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_bank_card.html
# Run it (after `pip install z3-solver numpy`) with:
#   python session1_bank_card.py

import z3


def create_model(instance):
    """A bank card has a four-digit PIN abcd: no two digits are the same, the
    two-digit number cd is 3 times ab, and da is 2 times bc."""
    # The puzzle has no instance data: the clues are the problem statement.

    # The four digits of the PIN, a b c d
    a, b, c, d = digits = [z3.Int(name) for name in "abcd"]

    solver = z3.Solver()

    # Each digit is from 0 to 9.
    solver.add([z3.And(0 <= digit, digit <= 9) for digit in digits])

    # No two digits are the same.
    solver.add(z3.Distinct(digits))

    # The two-digit number cd is 3 times the two-digit number ab.
    solver.add(10 * c + d == 3 * (10 * a + b))

    # The two-digit number da is 2 times the two-digit number bc.
    solver.add(10 * d + a == 2 * (10 * b + c))

    return solver, {"a": a, "b": b, "c": c, "d": d}


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
