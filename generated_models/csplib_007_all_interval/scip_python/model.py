# csplib_007_all_interval: a SCIP (Python) model from DCP Rosetta.
# Download the `csplib_007_all_interval.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_007_all_interval.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python csplib_007_all_interval.py csplib_007_all_interval.json

import numpy as np
from pyscipopt import Model, SCIP_PARAMEMPHASIS


def create_model(instance):
    """An all-interval series of size n: arrange the pitch classes 0, 1, ..., n-1 in a row x so
    that each occurs once, and so that the n-1 steps between neighbouring entries,
    diffs[i] = |x[i+1] - x[i]|, are each of the sizes 1, ..., n-1 exactly once.
    The model has no objective: any such series is a solution."""
    n = instance["n"]  # the number of pitch classes, and the length of the series (which has n-1 steps)
    sizes = np.arange(1, n)  # the possible step sizes, 1 to n-1: the statement's range for the intervals

    model = Model("all_interval")
    # With no objective, the solver should look for a series rather than work at proving optimality.
    model.setEmphasis(SCIP_PARAMEMPHASIS.FEASIBILITY)

    # b[i, v] is 1 when position i of the series holds pitch class v, and 0 when not.
    b = model.addMatrixVar((n, n), vtype="B", name="b")
    # each position holds exactly one pitch class
    model.addMatrixCons(b.sum(axis=1) == 1)
    # each pitch class 0, ..., n-1 is at exactly one position. SCIP has no all-different constraint,
    # so the permutation is written as this one-hot table, with the row and column sums of 1.
    model.addMatrixCons(b.sum(axis=0) == 1)
    # x[i] is the pitch class at position i: the value picked out by the one-hot row b[i]
    x = (b * np.arange(n)).sum(axis=1)

    # Step i joins position i to position i+1, and is a rise or a fall by one size k.
    # rise[i, k-1] is 1 when step i rises by k, and fall[i, k-1] is 1 when it falls by k.
    rise = model.addMatrixVar((n - 1, n - 1), vtype="B", name="rise")
    fall = model.addMatrixVar((n - 1, n - 1), vtype="B", name="fall")
    # each step is exactly one rise or fall, by exactly one size
    model.addMatrixCons(rise.sum(axis=1) + fall.sum(axis=1) == 1)
    # each size 1, ..., n-1 is taken by exactly one step, rising or falling: the sizes are a permutation
    model.addMatrixCons(rise.sum(axis=0) + fall.sum(axis=0) == 1)
    # Fixing all the steps fixes the series apart from its first entry, so the solver branches on the steps first.
    for var in list(rise.flatten()) + list(fall.flatten()):
        model.chgVarBranchPriority(var, 1)

    # Link the steps to the positions. For each size k, the two matrix constraints below give, for
    # every position i and pitch class v:
    #   if step i rises by k and position i holds v, then position i+1 holds v + k;
    #   if step i falls by k and position i holds v, then position i+1 holds v - k;
    #   a step cannot start from a pitch class that would leave the range 0, ..., n-1.
    # Each "if both are 1, then" is written as the linear inequality "b[i+1, w] >= b[i, v] + step - 1".
    for k in sizes:
        rising = rise[:, k - 1:k]  # column of the rise binaries for size k, one row per step
        falling = fall[:, k - 1:k]  # column of the fall binaries for size k
        model.addMatrixCons(b[:-1, :n - k] + rising - 1 <= b[1:, k:])
        model.addMatrixCons(b[:-1, n - k:] + rising <= 1)
        model.addMatrixCons(b[:-1, k:] + falling - 1 <= b[1:, :n - k])
        model.addMatrixCons(b[:-1, :k] + falling <= 1)

    # diffs[i] is the size of step i, whichever way it goes
    diffs = ((rise + fall) * sizes).sum(axis=1)

    return model, {"diffs": diffs, "x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
