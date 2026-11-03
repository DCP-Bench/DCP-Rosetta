# csplib_084_hadamard_matrix: a SCIP (Python) model from DCP Rosetta.
# Download the `csplib_084_hadamard_matrix.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_084_hadamard_matrix.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python csplib_084_hadamard_matrix.py csplib_084_hadamard_matrix.json

from pyscipopt import Model, quicksum


def create_model(instance):
    """Hadamard matrix Legendre pairs: find two sequences a and b, each of length l
    whose values are -1 or +1, such that for every shift s = 1..m the periodic autocorrelations
    of a and b add up to -2, and each sequence sums to 1. The length l is odd, and
    m = (l - 1) / 2."""
    l = instance["l"]  # the length of both sequences, an odd positive integer (from the statement)
    m = (l - 1) // 2   # the number of shifts constrained, m = (l - 1) / 2 (from the statement)

    model = Model("csplib_084_hadamard_matrix")

    # x_a[i] is 1 when a_i = +1 and 0 when a_i = -1 (0-based i); x_b likewise for b.
    # The two-value domain {-1, +1} is written as a binary: a_i = 2 * x_a[i] - 1.
    x_a = [model.addVar(f"x_a_{i}", vtype="B") for i in range(l)]
    x_b = [model.addVar(f"x_b_{i}", vtype="B") for i in range(l)]

    # same_a[k, i] is 1 when a_i equals a_{i+s} (indices mod l) for shift s = k + 1,
    # and 0 when they differ. The product a_i * a_{i+s} is then 2 * same_a[k, i] - 1 (likewise for b).
    # Such products are not linear in the binaries, so each one gets its own binary.
    same_a = model.addMatrixVar((m, l), vtype="B", name="same_a")
    same_b = model.addMatrixVar((m, l), vtype="B", name="same_b")

    # Parity: addConsXor(..., True) requires x[i] + x[j] + same[k, i] to be odd.
    # That forces same[k, i] = 1 when the two bits are equal and 0 when they differ.
    for x, same in ((x_a, same_a), (x_b, same_b)):
        for k in range(m):
            s = k + 1
            for i in range(l):
                j = (i + s) % l  # the periodic index: i + s wraps around modulo l
                model.addConsXor([x[i], x[j], same[k, i]], True)

    # Periodic autocorrelation constraints, one per shift s = 1..m:
    # PAF(A, s) + PAF(B, s) = -2. Each PAF is a sum of l products, and each product
    # is 2 * same - 1, so PAF(A, s) = 2 * (number of equal pairs) - l.
    paf_a = 2 * same_a.sum(axis=1) - l
    paf_b = 2 * same_b.sum(axis=1) - l
    model.addMatrixCons(paf_a + paf_b == -2)

    # Each sequence sums to 1: sum of (2 * x - 1) over the sequence equals 1.
    model.addCons(quicksum(2 * x - 1 for x in x_a) == 1)
    model.addCons(quicksum(2 * x - 1 for x in x_b) == 1)

    # The outputs a and b are the two sequences of -1/+1 values, each of length l.
    a = [2 * x - 1 for x in x_a]
    b = [2 * x - 1 for x in x_b]

    return model, {"a": a, "b": b}


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
