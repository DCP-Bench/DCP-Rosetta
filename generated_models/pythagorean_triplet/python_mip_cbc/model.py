# pythagorean_triplet: a Python-MIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/pythagorean_triplet.html
# Run it (after `pip install mip numpy`) with:
#   python pythagorean_triplet.py

import mip


def pick_value(model, name, lo, hi):
    # x is a whole number from lo to hi, and picks[v] is 1 for the value v that x takes
    picks = {v: model.add_var(f"{name}_is_{v}", var_type=mip.BINARY) for v in range(lo, hi + 1)}
    x = model.add_var(name, lb=lo, ub=hi, var_type=mip.INTEGER)
    # Exactly one value is picked, and x is that value.
    model.add_constr(mip.xsum(picks.values()) == 1)
    model.add_constr(x == mip.xsum(v * p for v, p in picks.items()))
    return x, picks


def create_model(instance):
    """Find natural numbers a < b < c with a^2 + b^2 = c^2 whose sum a + b + c is 1000."""
    total = 1000  # the sum a + b + c

    # Largest possible values, from a >= 1, a < b < c and a + b + c = total:
    # a is at most (total - 3) / 3, b at most (total - 2) / 2, c at most total - 3.
    a_max = (total - 3) // 3
    b_max = (total - 2) // 2
    c_max = total - 3

    model = mip.Model(solver_name="CBC")

    # a, b and c: the three numbers of the triplet
    a, a_pick = pick_value(model, "a", 1, a_max)
    b, b_pick = pick_value(model, "b", 2, b_max)
    c, c_pick = pick_value(model, "c", 3, c_max)

    # The numbers increase: a < b < c.
    model.add_constr(a + 1 <= b)
    model.add_constr(b + 1 <= c)

    # The three numbers add up to the total.
    model.add_constr(a + b + c == total)

    # a squared, b squared and c squared, read from the values picked for a, b and c.
    square_a = mip.xsum(v * v * p for v, p in a_pick.items())
    square_b = mip.xsum(v * v * p for v, p in b_pick.items())
    square_c = mip.xsum(v * v * p for v, p in c_pick.items())

    # The squares satisfy a^2 + b^2 = c^2.
    model.add_constr(square_a + square_b == square_c)

    return model, {"a": a, "b": b, "c": c}


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
