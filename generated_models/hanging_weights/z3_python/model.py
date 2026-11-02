# hanging_weights: a Z3 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/hanging_weights.html
# Run it (after `pip install z3-solver numpy`) with:
#   python hanging_weights.py

import z3


def create_model(instance):
    """Thirteen weights A to M, each an integer from 1 to 13, hang from a system of
    bars. Find the weights that make every pivot balance, where the weights on either
    side of a pivot are equal when weighted by their distance from the pivot."""
    max_weight = 13  # the largest weight; the smallest is 1

    # a to m are the weights A to M.
    a, b, c, d, e, f, g, h, i, j, k, l, m = weights = z3.Ints("a b c d e f g h i j k l m")

    solver = z3.Solver()

    # Each weight is an integer from 1 to 13, and no two weights are equal.
    solver.add([z3.And(w >= 1, w <= max_weight) for w in weights])
    solver.add(z3.Distinct(weights))

    # Bottom bars: the weights on either side of the pivot balance when weighted by
    # their distance from it.
    solver.add(4 * a == b, 5 * c == d, 3 * e == 2 * f)

    # A bar hanging under another bar counts as one weight equal to its total load.
    # The bar holding G has the C-D bar hanging from it.
    solver.add(3 * g == 2 * (c + d))
    # The bar holding J and K has the A-B bar and the G bar (with C and D) hanging from it.
    solver.add(3 * (a + b) + 2 * j == k + 2 * (g + c + d))
    # The bar holding H and I has the E-F bar hanging from it.
    solver.add(3 * h == 2 * (e + f) + 3 * i)
    # The bar holding L and M has the H-I bar (with E and F) hanging from it.
    solver.add(h + i + e + f == l + 4 * m)

    # The top bar balances the L-M side against the J-K side.
    solver.add(4 * (l + m + h + i + e + f) == 3 * (j + k + g + a + b + c + d))

    return solver, {"a": a, "b": b, "c": c, "d": d, "e": e, "f": f, "g": g,
                    "h": h, "i": i, "j": j, "k": k, "l": l, "m": m}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
