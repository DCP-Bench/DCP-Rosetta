# pythagorean_triplet: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/pythagorean_triplet.html
# Run it (after `pip install ortools`) with:
#   python pythagorean_triplet.py

from ortools.sat.python import cp_model


def create_model(instance):
    """Find the Pythagorean triplet a, b, c of natural numbers with a^2 + b^2 = c^2
    whose three members add up to 1000."""
    model = cp_model.CpModel()

    # a, b and c are the three members of the triplet. Each is at most 500: c is the
    # largest member, and the three add up to 1000, so c is below 500.
    a = model.new_int_var(1, 500, "a")
    b = model.new_int_var(1, 500, "b")
    c = model.new_int_var(1, 500, "c")

    # The three members add up to 1000.
    model.add(a + b + c == 1000)

    # aa, bb and cc are the squares of a, b and c.
    aa = model.new_int_var(1, 500 * 500, "aa")
    bb = model.new_int_var(1, 500 * 500, "bb")
    cc = model.new_int_var(1, 500 * 500, "cc")
    model.add_multiplication_equality(aa, [a, a])
    model.add_multiplication_equality(bb, [b, b])
    model.add_multiplication_equality(cc, [c, c])

    # The squares satisfy a^2 + b^2 = c^2.
    model.add(aa + bb == cc)

    return model, {"a": a, "b": b, "c": c}


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
