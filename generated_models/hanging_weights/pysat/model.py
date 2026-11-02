# hanging_weights: a PySAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/hanging_weights.html
# Run it (after `pip install "python-sat[pblib]" numpy`) with:
#   python hanging_weights.py

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Thirteen weights, A to M, each a whole number from 1 to 13, hang from a system
    of bars. Find the weights that make every bar balance: on either side of a pivot,
    each weight times its distance from the pivot is the same, and a bar hanging under
    another bar counts as one weight equal to its total."""
    pool = IDPool()
    # w[name] is the weight of the object with that letter.
    w = {name: Integer(name, 1, 13, vpool=pool) for name in "abcdefghijklm"}
    a, b, c, d, e, f, g, h, i, j, k, l, m = (w[name] for name in "abcdefghijklm")
    engine = IntegerEngine(vars=list(w.values()), vpool=pool)

    # The thirteen weights are all different.
    engine.add_alldifferent(list(w.values()))

    # The bottom right bar balances: 5 * C = D.
    engine.add_linear(5 * c == d)
    # The bottom left bar balances: 4 * A = B.
    engine.add_linear(4 * a == b)
    # The bar holding E and F balances: 3 * E = 2 * F.
    engine.add_linear(3 * e == 2 * f)
    # The bar holding G balances, with the bar holding C and D hanging under it as one
    # weight: 3 * G = 2 * (C + D).
    engine.add_linear(3 * g == 2 * c + 2 * d)
    # The bar holding J and K balances, with the A-B bar and the G bar hanging from it.
    engine.add_linear(3 * a + 3 * b + 2 * j == k + 2 * g + 2 * c + 2 * d)
    # The bar holding H and I balances, with the E-F bar hanging from it.
    engine.add_linear(3 * h == 2 * e + 2 * f + 3 * i)
    # The bar holding L and M balances, with the H-I bar hanging from it.
    engine.add_linear(h + i + e + f == l + 4 * m)
    # The top bar balances the L-M side against the J-K side.
    engine.add_linear(4 * l + 4 * m + 4 * h + 4 * i + 4 * e + 4 * f
                      == 3 * j + 3 * k + 3 * g + 3 * a + 3 * b + 3 * c + 3 * d)

    return engine.clausify(), w


if __name__ == "__main__":
    import numpy as np
    from pysat.solvers import Solver

    formula, outputs = create_model({})

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
