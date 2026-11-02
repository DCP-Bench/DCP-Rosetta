# hanging_weights: a PuLP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/hanging_weights.html
# Run it (after `pip install pulp numpy`) with:
#   python hanging_weights.py

import pulp


def create_model(instance):
    """Thirteen weights A to M, each an integer from 1 to 13, hang from a system of
    bars. Find the weights that make every pivot balance, where the weights on either
    side of a pivot are equal when weighted by their distance from the pivot."""
    # The weights, named a to m.
    names = "abcdefghijklm"
    # The number of weights, each of which takes a different value from 1 to n_weights.
    n_weights = 13
    values = range(1, n_weights + 1)

    problem = pulp.LpProblem("hanging_weights", pulp.LpMinimize)

    # has_value[w][v] is 1 when weight w is v, and 0 when not.
    has_value = {w: {v: pulp.LpVariable(f"has_value_{w}_{v}", cat="Binary") for v in values}
                 for w in names}

    # The value of each weight, a to m.
    a, b, c, d, e, f, g, h, i, j, k, l, m = (
        pulp.lpSum(v * has_value[w][v] for v in values) for w in names)

    # Each weight has exactly one value.
    for w in names:
        problem += pulp.lpSum(has_value[w].values()) == 1

    # The weights are all different, so each value is taken by exactly one weight.
    for v in values:
        problem += pulp.lpSum(has_value[w][v] for w in names) == 1

    # The bottom left bar balances: 4 times A equals B.
    problem += 4 * a == b

    # The bottom right bar balances: 5 times C equals D.
    problem += 5 * c == d

    # The bar holding E and F balances: 3 times E equals 2 times F.
    problem += 3 * e == 2 * f

    # The bar holding G balances with the C-D bar hanging under it, which counts as one weight.
    problem += 3 * g == 2 * (c + d)

    # The bar holding J and K balances, with the A-B bar and the G bar hanging from it.
    problem += 3 * (a + b) + 2 * j == k + 2 * (g + c + d)

    # The bar holding H and I balances, with the E-F bar hanging from it.
    problem += 3 * h == 2 * (e + f) + 3 * i

    # The bar holding L and M balances, with the H-I bar (with E and F) hanging from it.
    problem += h + i + e + f == l + 4 * m

    # The top bar balances the L-M side against the J-K side.
    problem += 4 * (l + m + h + i + e + f) == 3 * (j + k + g + a + b + c + d)

    return problem, dict(zip(names, (a, b, c, d, e, f, g, h, i, j, k, l, m)))


if __name__ == "__main__":
    import numpy as np

    problem, outputs = create_model({})
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
