# hanging_weights: a Python-MIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/hanging_weights.html
# Run it (after `pip install mip numpy`) with:
#   python hanging_weights.py

import mip


def create_model(instance):
    """Thirteen weights, A to M, each a whole number from 1 to 13, hang from a system of
    bars. Choose the weights so that every bar balances: the weights on either side of a
    pivot must match when each is multiplied by its distance from the pivot. A bar hanging
    under another bar counts as one weight equal to its total."""
    model = mip.Model(solver_name="CBC")

    # The values a weight can take.
    values = range(1, 14)
    names = "abcdefghijklm"

    # takes[n, v] is 1 when weight n is v, and 0 when not.
    takes = {}
    for n in names:
        for v in values:
            takes[n, v] = model.add_var(f"takes_{n}_{v}", var_type=mip.BINARY)
    # weight[n] is the value of weight n.
    weight = {}
    for n in names:
        weight[n] = model.add_var(n, lb=values[0], ub=values[-1], var_type=mip.INTEGER)

    # Each weight is exactly one value, and weight[n] is that value.
    for n in names:
        model.add_constr(mip.xsum(takes[n, v] for v in values) == 1)
        model.add_constr(weight[n] == mip.xsum(v * takes[n, v] for v in values))
    # The weights all differ, so each value is taken by at most one weight.
    for v in values:
        model.add_constr(mip.xsum(takes[n, v] for n in names) <= 1)

    # The weights by letter.
    a, b, c, d, e, f, g = (weight[n] for n in "abcdefg")
    h, i, j, k, l, m = (weight[n] for n in "hijklm")

    # Bar AB: A hangs at distance 4 on the left and B at distance 1 on the right.
    model.add_constr(4 * a == b)

    # Bottom right bar: 5 * C = D, as the description gives.
    model.add_constr(5 * c == d)

    # Bar EF: E hangs at distance 3 and F at distance 2 from the pivot.
    model.add_constr(3 * e == 2 * f)

    # Bar G: the bar holding C and D hangs from G's bar at distance 2, with G at distance 3.
    model.add_constr(3 * g == 2 * (c + d))

    # Bar JK: on the left, J at distance 2 and the AB bar (total A + B) at distance 3.
    # On the right, K at distance 1 and the G bar (total G + C + D) at distance 2.
    model.add_constr(3 * (a + b) + 2 * j == k + 2 * (g + c + d))

    # Bar HI: H at distance 3 on the left. On the right, the EF bar (total E + F) at
    # distance 2 and I at distance 3.
    model.add_constr(3 * h == 2 * (e + f) + 3 * i)

    # Bar LM: on the left, the HI bar (total H + I + E + F) at distance 1. On the right,
    # L at distance 1 and M at distance 4.
    model.add_constr(h + i + e + f == l + 4 * m)

    # Top bar: on the left, the LM bar (total L + M + H + I + E + F) at distance 4. On the
    # right, the JK bar (total J + K + G + A + B + C + D) at distance 3.
    model.add_constr(4 * (l + m + h + i + e + f) == 3 * (j + k + g + a + b + c + d))

    # No objective: the balance conditions alone decide the weights.
    return model, {n: weight[n] for n in names}


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
