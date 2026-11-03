# five_brigands: a Z3 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/five_brigands.html
# Run it (after `pip install z3-solver numpy`) with:
#   python five_brigands.py

import z3


def create_model(instance):
    """Five Spanish brigands, Alfonso, Benito, Carlos, Diego and Esteban, have
    captured exactly 200 doubloons altogether. If Alfonso had twelve times as
    much, Benito three times as much, Carlos the same amount, Diego half as
    much and Esteban one third as much, they would still have 200 doubloons
    altogether. No brigand has less than one doubloon. How many doubloons has
    each?"""
    total = 200  # the doubloons the brigands have altogether

    # A, B, C, D and E are the doubloons of Alfonso, Benito, Carlos, Diego and Esteban.
    a, b, c, d, e = z3.Ints("A B C D E")

    solver = z3.Solver()

    # Each brigand has at least one doubloon, and at most all of them.
    solver.add([z3.And(1 <= v, v <= total) for v in (a, b, c, d, e)])

    # Together they have all the doubloons.
    solver.add(a + b + c + d + e == total)

    # With the changed amounts they still have the total. Multiplied by 6 to
    # clear the fractions in D/2 and E/3.
    solver.add(6 * (12 * a + 3 * b + c) + 3 * d + 2 * e == 6 * total)

    return solver, {"A": a, "B": b, "C": c, "D": d, "E": e}


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
