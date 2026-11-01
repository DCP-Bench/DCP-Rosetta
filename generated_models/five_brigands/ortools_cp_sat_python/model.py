# five_brigands: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/five_brigands.html
# Run it (after `pip install ortools`) with:
#   python five_brigands.py

from ortools.sat.python import cp_model


def create_model(instance):
    """Five Spanish brigands, Alfonso, Benito, Carlos, Diego and Esteban, have
    captured exactly 200 doubloons altogether. If Alfonso had twelve times as
    much, Benito three times as much, Carlos the same amount, Diego half as
    much and Esteban one third as much, they would still have 200 doubloons
    altogether. No brigand has less than one doubloon. How many has each?"""
    total = 200  # the doubloons the brigands have altogether

    model = cp_model.CpModel()

    # A, B, C, D and E are the doubloons of Alfonso, Benito, Carlos, Diego and Esteban.
    # Each brigand has at least one doubloon.
    a, b, c, d, e = [model.new_int_var(1, total, name) for name in "ABCDE"]

    # Together they have all the doubloons.
    model.add(a + b + c + d + e == total)
    # With the changed amounts they still have the total: 12A + 3B + C + D/2 + E/3 = total, times 6.
    model.add(72 * a + 18 * b + 6 * c + 3 * d + 2 * e == 6 * total)

    return model, {"A": a, "B": b, "C": c, "D": d, "E": e}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
