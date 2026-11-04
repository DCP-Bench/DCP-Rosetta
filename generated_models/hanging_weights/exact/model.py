# hanging_weights: an Exact (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/hanging_weights.html
# Run it (after `pip install exact numpy`) with:
#   python hanging_weights.py

from exact import Exact


def create_model(instance):
    """Thirteen weights, A to M, each an integer from 1 to 13 and all different, hang from a
    system of bars. Find the weights that make every bar balance."""
    names = list("abcdefghijklm")  # the weights A to M

    solver = Exact()

    # Exact identifies its variables by name.
    # Each weight is an integer from 1 to 13.
    for name in names:
        solver.addVariable(name, 1, 13)

    # is_value[name][v] is 1 when the weight has value v, and 0 when not.
    is_value = {name: {v: f"{name}_is_{v}" for v in range(1, 14)} for name in names}
    for name in names:
        for v in range(1, 14):
            solver.addVariable(is_value[name][v], 0, 1)
        # Each weight has exactly one value.
        solver.addConstraint([(1, is_value[name][v]) for v in range(1, 14)], True, 1, True, 1)
        # The weight is the value it has.
        solver.addConstraint([(v, is_value[name][v]) for v in range(1, 14)] + [(-1, name)],
                             True, 0, True, 0)
    # The weights are all different: each value is used by at most one weight.
    for v in range(1, 14):
        solver.addConstraint([(1, is_value[name][v]) for name in names], False, 0, True, 1)

    # Every bar balances: the weights on one side, each times its distance from the pivot,
    # equal those on the other side. A bar hanging under another counts as one weight, its total.
    balances = [
        # the bottom left bar
        [(4, "a"), (-1, "b")],
        # the bottom right bar
        [(5, "c"), (-1, "d")],
        # the bar holding E and F
        [(3, "e"), (-2, "f")],
        # the bar holding G, with the C-D bar hanging from it
        [(3, "g"), (-2, "c"), (-2, "d")],
        # the bar holding J and K, with the A-B bar and the G bar hanging from it
        [(3, "a"), (3, "b"), (2, "j"), (-1, "k"), (-2, "g"), (-2, "c"), (-2, "d")],
        # the bar holding H and I, with the E-F bar hanging from it
        [(3, "h"), (-2, "e"), (-2, "f"), (-3, "i")],
        # the bar holding L and M, with the H-I bar hanging from it
        [(1, "h"), (1, "i"), (1, "e"), (1, "f"), (-1, "l"), (-4, "m")],
        # the top bar: the L-M side against the J-K side
        [(4, "l"), (4, "m"), (4, "h"), (4, "i"), (4, "e"), (4, "f"),
         (-3, "j"), (-3, "k"), (-3, "g"), (-3, "a"), (-3, "b"), (-3, "c"), (-3, "d")],
    ]
    for terms in balances:
        solver.addConstraint(terms, True, 0, True, 0)

    # The weight of each letter.
    return solver, {name: name for name in names}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
