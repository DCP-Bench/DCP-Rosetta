# csplib_028_bibd: a SCIP (Python) model from DCP Rosetta.
# Download the `csplib_028_bibd.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_028_bibd.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python csplib_028_bibd.py csplib_028_bibd.json

from itertools import combinations

from pyscipopt import Model


def create_model(instance):
    """Balanced Incomplete Block Design: arrange v distinct objects into b blocks
    so that each block holds exactly k distinct objects, each object lies in
    exactly r blocks, and every two distinct objects lie together in exactly l
    blocks. The output is the v-by-b incidence matrix: entry [i][j] is 1 when
    object i is in block j, and 0 when not."""
    v = instance["v"]    # number of objects
    b = instance["b"]    # number of blocks
    r = instance["r"]    # number of blocks each object lies in
    k = instance["k"]    # number of objects each block holds
    lam = instance["l"]  # number of blocks that every pair of objects shares

    model = Model("bibd")

    # x[i, j] is 1 when object i is in block j, and 0 when not
    x = model.addMatrixVar((v, b), vtype="B", name="x")

    # Each object lies in exactly r blocks: every row of x has r ones.
    model.addMatrixCons(x.sum(axis=1) == r)

    # Each block holds exactly k objects: every column of x has k ones.
    model.addMatrixCons(x.sum(axis=0) == k)

    # Pairs of objects, one row of `both` per pair. both[p, j] is 1 when both
    # objects of pair p are in block j. The AND is stated with addConsAnd, which
    # ties both[p, j] to the product x[i, j] * x[i2, j] in both directions, since
    # SCIP has no product of two binaries in a linear constraint.
    pairs = list(combinations(range(v), 2))
    both = model.addMatrixVar((len(pairs), b), vtype="B", name="both")
    for p, (i, i2) in enumerate(pairs):
        for j in range(b):
            model.addConsAnd([x[i, j], x[i2, j]], both[p, j])

    # Every two distinct objects lie together in exactly l blocks: each pair's
    # row of `both` has l ones, so the blocks they share number exactly l.
    model.addMatrixCons(both.sum(axis=1) == lam)

    return model, {"matrix": x}


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
