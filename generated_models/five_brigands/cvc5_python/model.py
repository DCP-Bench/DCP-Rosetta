# five_brigands: a cvc5 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/five_brigands.html
# Run it (after `pip install cvc5 numpy`) with:
#   python five_brigands.py

import cvc5.pythonic as c5


def create_model(instance):
    """Five brigands, Alfonso, Benito, Carlos, Diego and Esteban, captured
    exactly 200 doubloons altogether. If Alfonso had twelve times as much,
    Benito three times as much, Carlos the same amount, Diego half as much and
    Esteban one third as much, they would still have 200 doubloons altogether.
    No brigand had less than one doubloon. How many had each?"""
    # The doubloons of Alfonso, Benito, Carlos, Diego and Esteban
    A, B, C, D, E = c5.Ints("A B C D E")
    outputs = {"A": A, "B": B, "C": C, "D": D, "E": E}

    solver = c5.Solver()

    # No brigand had less than one doubloon.
    solver.add(A >= 1, B >= 1, C >= 1, D >= 1, E >= 1)

    # The brigands captured altogether exactly 200 doubloons.
    solver.add(A + B + C + D + E == 200)

    # With Alfonso's share taken twelve times, Benito's three times, Carlos's
    # unchanged, Diego's halved and Esteban's a third, the total is still 200.
    # Both sides are multiplied by 6 to avoid fractions.
    solver.add(72 * A + 18 * B + 6 * C + 3 * D + 2 * E == 1200)

    return solver, outputs


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
