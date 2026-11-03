# hanging_weights: a SCIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/hanging_weights.html
# Run it (after `pip install pyscipopt numpy`) with:
#   python hanging_weights.py

from pyscipopt import Model


def create_model(instance):
    """Thirteen weights, A to M, hang from a system of bars. Each weight is an
    integer from 1 to 13. Find the weights that balance the diagram: on every
    bar, the weights on each side of its pivot, each multiplied by its distance
    from the pivot, are equal; and a bar hanging from another bar counts as one
    weight, equal to the total of the weights on it.

    The instance file is empty ([]), so the statement fixes every number used
    here, and the instance argument is not read.
    """
    model = Model("hanging_weights")

    # Distances are counted in bar segments of the diagram: one segment is one
    # "+--" step along a bar. Each bar's pivot is the mark where the stem from
    # the bar above reaches it; where a stem falls between two marks, the pivot
    # is the nearer mark.

    # Each weight is an integer from 1 to 13 (the statement).
    a = model.addVar("a", vtype="I", lb=1, ub=13)  # A: left end of the bottom-left bar
    b = model.addVar("b", vtype="I", lb=1, ub=13)  # B: right end of the bottom-left bar
    c = model.addVar("c", vtype="I", lb=1, ub=13)  # C: left end of the bottom-right bar
    d = model.addVar("d", vtype="I", lb=1, ub=13)  # D: right end of the bottom-right bar
    e = model.addVar("e", vtype="I", lb=1, ub=13)  # E: left end of the lower-left bar
    f = model.addVar("f", vtype="I", lb=1, ub=13)  # F: right end of the lower-left bar
    g = model.addVar("g", vtype="I", lb=1, ub=13)  # G: left end of the middle-right bar
    h = model.addVar("h", vtype="I", lb=1, ub=13)  # H: left end of the upper-left bar
    i = model.addVar("i", vtype="I", lb=1, ub=13)  # I: right end of the upper-left bar
    j = model.addVar("j", vtype="I", lb=1, ub=13)  # J: on the bar with J and K, left of its pivot
    k = model.addVar("k", vtype="I", lb=1, ub=13)  # K: on the bar with J and K, right of its pivot
    l = model.addVar("l", vtype="I", lb=1, ub=13)  # L: on the bar with L and M, right of its pivot
    m = model.addVar("m", vtype="I", lb=1, ub=13)  # M: right end of the bar with L and M

    # Total weights of the bars that hang from other bars. Each is a plain sum
    # of the weights on that bar and the bars below it.
    ef = e + f                # the lower-left bar (E and F)
    hi_bar = h + i + ef       # the upper-left bar, with the lower-left bar hanging from it
    lm_bar = hi_bar + l + m   # the bar with L and M, with the upper-left bar hanging from it
    ab = a + b                # the bottom-left bar (A and B)
    cd = c + d                # the bottom-right bar (C and D)
    gbar = g + cd             # the middle-right bar, with the bottom-right bar hanging from it
    jk = ab + j + k + gbar    # the bar with J and K, with the bottom-left and middle-right bars hanging from it

    # Lower-left bar: E is 3 segments left of its pivot and F is 2 segments right.
    model.addCons(3 * e == 2 * f)

    # Upper-left bar: H is 3 segments left of its pivot; the lower-left bar hangs
    # 2 segments right and I is 3 segments right.
    model.addCons(3 * h == 2 * ef + 3 * i)

    # Bar with L and M: the upper-left bar hangs 1 segment left of its pivot;
    # L is 1 segment right and M is 4 segments right.
    model.addCons(hi_bar == l + 4 * m)

    # Top bar: the bar with L and M hangs 4 segments left of its pivot and the
    # bar with J and K hangs 3 segments right.
    model.addCons(4 * lm_bar == 3 * jk)

    # Bottom-left bar: A is 4 segments left of its pivot and B is 1 segment right.
    model.addCons(4 * a == b)

    # Bottom-right bar: C is 5 segments left of its pivot and D is 1 segment right.
    model.addCons(5 * c == d)

    # Middle-right bar: G is 3 segments left of its pivot and the bottom-right
    # bar hangs 2 segments right.
    model.addCons(3 * g == 2 * cd)

    # Bar with J and K: the bottom-left bar hangs 3 segments left of its pivot,
    # J is 2 segments left, K is 1 segment right and the middle-right bar hangs
    # 2 segments right.
    model.addCons(3 * ab + 2 * j == k + 2 * gbar)

    # No objective: the puzzle asks for weights that balance, not for the best ones.
    outputs = {"a": a, "b": b, "c": c, "d": d, "e": e, "f": f, "g": g,
               "h": h, "i": i, "j": j, "k": k, "l": l, "m": m}
    return model, outputs


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
