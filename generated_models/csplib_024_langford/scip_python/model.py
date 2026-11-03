# csplib_024_langford: a SCIP (Python) model from DCP Rosetta.
# Download the `csplib_024_langford.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_024_langford.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python csplib_024_langford.py csplib_024_langford.json

import numpy as np
from pyscipopt import Model, quicksum


def create_model(instance):
    """Langford's problem: take two copies of each number 1 to k and arrange
    the 2k numbers in one sequence, so that the two copies of number v have
    exactly v numbers between them (their positions differ by v + 1).
    The sequence is returned as sol, one number per position, numbered from 1."""
    k = instance["k"]  # the largest number: the numbers 1..k each appear twice
    n = 2 * k          # the sequence length: two copies of each of the k numbers

    model = Model("csplib_024_langford")

    # x[p, v - 1] is 1 when position p of the sequence holds number v, and 0 when not
    x = model.addMatrixVar((n, k), vtype="B", name="x")

    # Each position of the sequence holds exactly one number.
    model.addMatrixCons(x.sum(axis=1) == 1)

    # Each number 1..k appears exactly twice in the sequence.
    model.addMatrixCons(x.sum(axis=0) == 2)

    # The two copies of number v lie v + 1 positions apart. No general constraint of
    # SCIP states a fixed distance between two positions, so it is written per
    # position p: if number v sits at p, then one of the positions p - v - 1 and
    # p + v + 1 (those inside the sequence) must hold v too. Because v appears
    # exactly twice, that partner is the other copy, so the two copies are v + 1
    # apart. This needs one inequality per position and no auxiliary variables.
    for v in range(1, k + 1):
        for p in range(n):
            partners = [q for q in (p - v - 1, p + v + 1) if 0 <= q < n]
            model.addCons(x[p, v - 1] <= quicksum(x[q, v - 1] for q in partners))

    # sol[p] is the number at position p: row p of x has exactly one 1, in column v - 1,
    # and weighting column v - 1 by v picks out that number.
    sol = x @ np.arange(1, k + 1)

    # The problem asks for any arrangement, so the model has no objective.
    return model, {"sol": sol}


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
