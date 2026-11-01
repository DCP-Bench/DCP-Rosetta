# send_more_money: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/send_more_money.html
# Run it (after `pip install ortools`) with:
#   python send_more_money.py

from ortools.sat.python import cp_model


def create_model(instance):
    """Cryptarithmetic puzzle: give each letter a different digit so that
    SEND + MORE = MONEY holds."""
    model = cp_model.CpModel()

    # The digit that each letter stands for. The first letters of SEND and MORE are not zero.
    s, m = [model.new_int_var(1, 9, name) for name in "sm"]
    e, n, d, o, r, y = [model.new_int_var(0, 9, name) for name in "endory"]

    # Different letters take different digits.
    model.add_all_different([s, e, n, d, m, o, r, y])

    # SEND, MORE and MONEY, each read as a decimal number.
    send = 1000 * s + 100 * e + 10 * n + d
    more = 1000 * m + 100 * o + 10 * r + e
    money = 10000 * m + 1000 * o + 100 * n + 10 * e + y

    # The sum of SEND and MORE is MONEY.
    model.add(send + more == money)

    return model, {"s": s, "e": e, "n": n, "d": d, "m": m, "o": o, "r": r, "y": y}


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
