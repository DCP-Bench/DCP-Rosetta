# session1_bank_card: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_bank_card.html
# Run it (after `pip install ortools`) with:
#   python session1_bank_card.py

from ortools.sat.python import cp_model


def create_model(instance):
    """A bank card has a four-digit PIN abcd: no two digits are the same, the
    two-digit number cd is 3 times ab, and da is 2 times bc."""
    model = cp_model.CpModel()

    # The four digits of the PIN, a b c d
    a, b, c, d = [model.new_int_var(0, 9, name) for name in "abcd"]

    # No two digits are the same.
    model.add_all_different([a, b, c, d])

    # The two-digit number cd is 3 times the two-digit number ab.
    model.add(10 * c + d == 3 * (10 * a + b))

    # The two-digit number da is 2 times the two-digit number bc.
    model.add(10 * d + a == 2 * (10 * b + c))

    return model, {"a": a, "b": b, "c": c, "d": d}


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
