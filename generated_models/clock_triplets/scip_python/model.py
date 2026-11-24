# clock_triplets: a SCIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/clock_triplets.html
# Run it (after `pip install pyscipopt numpy`) with:
#   python clock_triplets.py

import numpy as np
from pyscipopt import Model


def create_model(instance):
    """Put the numbers 1 to 12 on the face of a clock, one per position, so that
    no three adjacent numbers add up to more than 21. The statement does not
    number the positions, so position 0 is the one at 12 o'clock and the others
    run clockwise from it. The face is a ring: the last position is next to the first.
    The instance file is empty ([]), so the statement fixes all the data and
    the instance argument is not read."""
    model = Model("clock_triplets")

    # b[p, v] is 1 when position p on the clock holds the number v + 1.
    # The clock has 12 positions and the numbers are 1 to 12 (from the statement).
    b = model.addMatrixVar((12, 12), vtype="B", name="b")

    # Each position holds exactly one number.
    model.addMatrixCons(b.sum(axis=1) == 1)
    # Each number sits on exactly one position: the numbers are a permutation.
    model.addMatrixCons(b.sum(axis=0) == 1)

    # x[p] is the number at position p: the value of its one chosen b[p, v].
    x = b @ np.arange(1, 13)

    # Any three adjacent positions p, p + 1, p + 2 (wrapping around the ring)
    # have a sum of at most 21 (the limit from the statement).
    model.addMatrixCons(x + np.roll(x, -1) + np.roll(x, -2) <= 21)

    return model, {"x": x}


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
