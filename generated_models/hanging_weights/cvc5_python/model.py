# hanging_weights: a cvc5 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/hanging_weights.html
# Run it (after `pip install cvc5 numpy`) with:
#   python hanging_weights.py

import cvc5.pythonic as c5


def create_model(instance):
    """Thirteen weights, A to M, hang from a system of bars. Each weight is a whole number
    from 1 to 13. Find the weights that make the diagram balance: at every pivot, the
    weights on the two sides are equal once each is multiplied by its distance from the
    pivot. A bar hanging beneath another bar counts as one weight, equal to its total."""
    # The weights A to M.
    a, b, c, d, e, f, g, h, i, j, k, l, m = c5.Ints("a b c d e f g h i j k l m")
    weights = [a, b, c, d, e, f, g, h, i, j, k, l, m]

    solver = c5.Solver()

    # Each weight is a whole number from 1 to 13.
    solver.add([w >= 1 for w in weights] + [w <= 13 for w in weights])

    # The total weight of each bar, with everything hanging beneath it.
    hi_total = h + i + e + f  # the bar with H and I, and the bar with E and F under it
    lm_total = hi_total + l + m  # the bar with L and M, and the bar with H and I under it
    jk_total = a + b + j + k + g + c + d  # the bar with J and K, and all weights under it

    # The top bar: the bar with L and M, at distance 4 from the pivot, balances the bar
    # with J and K, at distance 3.
    solver.add(4 * lm_total == 3 * jk_total)

    # The bar with L and M: the bar with H and I, at distance 1, balances L at distance 1
    # and M at distance 4.
    solver.add(hi_total == l + 4 * m)

    # The bar with H and I: H at distance 3 balances the bar with E and F at distance 2
    # and I at distance 3.
    solver.add(3 * h == 2 * (e + f) + 3 * i)

    # The bar with E and F: E at distance 3 balances F at distance 2.
    solver.add(3 * e == 2 * f)

    # The bar with J and K: the bar with A and B at distance 3 and J at distance 2 balance
    # K at distance 1 and the bar with G at distance 2.
    solver.add(3 * (a + b) + 2 * j == k + 2 * (g + c + d))

    # The bar with A and B: A at distance 4 balances B at distance 1.
    solver.add(4 * a == b)

    # The bar with G: G at distance 3 balances the bar with C and D at distance 2.
    solver.add(3 * g == 2 * (c + d))

    # The bar with C and D: C at distance 5 balances D at distance 1.
    solver.add(5 * c == d)

    # The weights, by letter.
    outputs = {"a": a, "b": b, "c": c, "d": d, "e": e, "f": f, "g": g,
               "h": h, "i": i, "j": j, "k": k, "l": l, "m": m}
    return solver, outputs


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
