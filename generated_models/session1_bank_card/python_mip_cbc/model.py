# session1_bank_card: a Python-MIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_bank_card.html
# Run it (after `pip install mip numpy`) with:
#   python session1_bank_card.py

import mip


def create_model(instance):
    """A bank card has a four-digit PIN abcd. No two digits are the same, the
    two-digit number cd is 3 times ab, and the two-digit number da is 2 times
    bc. Find the PIN."""
    # The puzzle has no instance data: the facts are the problem statement.

    model = mip.Model(solver_name="CBC")

    # The digits a, b, c and d of the PIN. The first digit is not 0, since ab is a two-digit number.
    a = model.add_var("a", lb=1, ub=9, var_type=mip.INTEGER)
    b = model.add_var("b", lb=0, ub=9, var_type=mip.INTEGER)
    c = model.add_var("c", lb=0, ub=9, var_type=mip.INTEGER)
    d = model.add_var("d", lb=0, ub=9, var_type=mip.INTEGER)
    digits = [a, b, c, d]  # the four digits in PIN order

    # No two digits are the same. For each pair, s is 0 when the earlier digit
    # is the smaller one, and 1 when it is the larger one.
    for i in range(4):
        for j in range(i + 1, 4):
            s = model.add_var(f"s_{i}_{j}", var_type=mip.BINARY)
            model += digits[i] - digits[j] <= -1 + 10 * s
            model += digits[j] - digits[i] <= -1 + 10 * (1 - s)

    # The two-digit number cd is 3 times the two-digit number ab.
    model += 10 * c + d == 3 * (10 * a + b)

    # The two-digit number da is 2 times the two-digit number bc.
    model += 10 * d + a == 2 * (10 * b + c)

    # No objective: any PIN that meets the facts answers the puzzle.
    return model, {"a": a, "b": b, "c": c, "d": d}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
