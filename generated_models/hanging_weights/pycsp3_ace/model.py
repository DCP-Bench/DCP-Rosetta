# hanging_weights: a PyCSP3 model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/hanging_weights.html
# Run it (after `pip install pycsp3`, which also needs Java for its ACE solver) with:
#   python hanging_weights.py

from pycsp3 import *


def create_model(instance):
    """Weights A to M hang from a system of bars so that the diagram balances. The
    weights are different integers from 1 to 13. On each bar the weights on either
    side of the pivot balance, weighted by their distance from the pivot, and a bar
    hanging beneath another counts as its total weight. Find the weights."""
    # Each three characters along a bar are one unit of distance; the distances
    # below are read from the diagram in those units.
    n_weights = 13
    # Each weight is a different integer from 1 to n_weights.
    a = Var(dom=range(1, n_weights + 1))  # weight A
    b = Var(dom=range(1, n_weights + 1))  # weight B
    c = Var(dom=range(1, n_weights + 1))  # weight C
    d = Var(dom=range(1, n_weights + 1))  # weight D
    e = Var(dom=range(1, n_weights + 1))  # weight E
    f = Var(dom=range(1, n_weights + 1))  # weight F
    g = Var(dom=range(1, n_weights + 1))  # weight G
    h = Var(dom=range(1, n_weights + 1))  # weight H
    i = Var(dom=range(1, n_weights + 1))  # weight I
    j = Var(dom=range(1, n_weights + 1))  # weight J
    k = Var(dom=range(1, n_weights + 1))  # weight K
    l = Var(dom=range(1, n_weights + 1))  # weight L
    m = Var(dom=range(1, n_weights + 1))  # weight M

    satisfy(
        # The weights are all different.
        AllDifferent([a, b, c, d, e, f, g, h, i, j, k, l, m]),
        # The bottom-left bar holds A and B: A hangs 4 units left of its pivot, B 1 unit right.
        4 * a == b,
        # The bottom-right bar holds C and D: C hangs 5 units left of its pivot, D 1 unit right.
        5 * c == d,
        # The bar holding G carries G 3 units left of its pivot, and the bar holding C and D 2 units right.
        3 * g == 2 * (c + d),
        # The bar holding E and F: E hangs 3 units left of its pivot, F 2 units right.
        3 * e == 2 * f,
        # The bar holding H and I: H is 3 units left of its pivot, I 3 units right, and the bar holding E and F 2 units right.
        3 * h == 3 * i + 2 * (e + f),
        # The bar holding L and M: the bar holding H, I, E and F (its total weight) is 1 unit left of its pivot,
        # L 1 unit right, and M 4 units right.
        h + i + e + f == l + 4 * m,
        # The bar holding J and K: J is 2 units left of its pivot, the bar holding A and B 3 units left,
        # K 1 unit right, and the bar holding G, C and D 2 units right.
        2 * j + 3 * (a + b) == k + 2 * (g + c + d),
        # The top bar: the bar holding L and M (with H, I, E and F) is 4 units left of the pivot,
        # and the bar holding J and K (with A to G) is 3 units right.
        4 * (h + i + e + f + l + m) == 3 * (j + k + a + b + g + c + d),
    )

    return {
        "a": a, "b": b, "c": c, "d": d, "e": e, "f": f, "g": g,
        "h": h, "i": i, "j": j, "k": k, "l": l, "m": m,
    }


if __name__ == "__main__":
    outputs = create_model({})
    if solve() is SAT:
        for name, variable in outputs.items():
            print(name, "=", value(variable))
    else:
        print("No solution:", status())
