# broken_weights: a SCIP (Python) model from DCP Rosetta.
# Download the `broken_weights.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/broken_weights.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python broken_weights.py broken_weights.json

import numpy as np
from pyscipopt import Model


def create_model(instance):
    """A merchant's measuring weight of m pounds broke into n pieces, each a whole
    number of pounds. Find the piece weights, adding up to m, so that the pieces
    weigh every whole number of pounds from 1 to m on a balance scale: the object
    goes on the left pan, and each piece goes on the right pan, on the left pan
    or off the scale."""
    m = instance["m"]  # the total weight in pounds: the pieces add up to it
    n = instance["n"]  # the number of pieces

    model = Model("broken_weights")

    # w[i] is the weight of piece i in pounds, a whole number. The lower bound 1 is
    # an assumption: a piece is a part of the weight, so it weighs at least one pound.
    # The upper bound m follows from the pieces adding up to m, each at least 1.
    w = model.addMatrixVar(n, vtype="I", lb=1, ub=m, name="w")

    # right[k, i] is 1 when piece i is on the right pan (opposite the object) in the
    # weighing of k+1 pounds; left[k, i] is 1 when it is on the left pan, with the
    # object. A piece on neither pan is off the scale for that weighing.
    right = model.addMatrixVar((m, n), vtype="B", name="right")
    left = model.addMatrixVar((m, n), vtype="B", name="left")

    # A piece is on at most one pan in each weighing.
    model.addMatrixCons(right + left <= 1)

    # on_right[k, i] is the weight piece i puts on the right pan in weighing k+1:
    # w[i] when it is there, else 0. on_left is the same for the left pan. Each is a
    # product of a binary and w[i], written as big-M constraints with M = m, the upper
    # bound of w, rather than with addConsIndicator: an indicator gives the LP
    # relaxation little to work with. Measured on the 80-pound instance, the indicator
    # version found no first solution in 170 s; this one found two solutions in 66 s,
    # or in 12 s with the branch priority below.
    on_right = model.addMatrixVar((m, n), vtype="I", lb=0, ub=m, name="on_right")
    on_left = model.addMatrixVar((m, n), vtype="I", lb=0, ub=m, name="on_left")
    for on, pan in ((on_right, right), (on_left, left)):
        model.addMatrixCons(on <= m * pan)            # 0 when the piece is not on this pan
        model.addMatrixCons(on <= w)                  # never more than the piece weighs
        model.addMatrixCons(on >= w - m * (1 - pan))  # the full weight when it is on this pan

    # The pieces weigh m pounds in total.
    model.addCons(w.sum() == m)

    # Every weight from 1 to m balances: the pieces on the right pan outweigh the
    # pieces on the left pan by exactly the object's weight. Row k is the weighing of
    # k+1 pounds, so the right-hand side is 1, 2, ..., m.
    model.addMatrixCons((on_right - on_left).sum(axis=1) == np.arange(1, m + 1))

    # Search hint only, no constraint: branch on the piece weights before the pan
    # choices. Once the weights are fixed, each weighing is a small pan choice. Measured
    # on the 80-pound instance, this took the two-solution time from 66 s to 12 s.
    for i in range(n):
        model.chgVarBranchPriority(w[i], 100)

    return model, {"weights": w}


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
