# csplib_049_number_partitioning: a SCIP (Python) model from DCP Rosetta.
# Download the `csplib_049_number_partitioning.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_049_number_partitioning.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python csplib_049_number_partitioning.py csplib_049_number_partitioning.json

import numpy as np
from pyscipopt import Model


def create_model(instance):
    """Number partitioning (CSPLib 049): split the numbers 1..n into two sets A and B
    that have the same size, the same sum and the same sum of squares. A and B are
    reported in increasing order, each as a list of n/2 numbers."""
    n = instance["n"]  # the numbers to partition are 1..n
    values = np.arange(1, n + 1)  # values[i] is the number i + 1
    half = n // 2  # the length of each output list (see the size constraint)

    model = Model("csplib_049_number_partitioning")

    # x[i] is 1 when the number i + 1 is in A, and 0 when it is in B
    x = model.addMatrixVar(n, vtype="B", name="x")

    # A and B together hold all n numbers and have the same size, so each has n / 2
    # numbers: the constraint is 2 * |A| = n, with |A| the sum of x. For odd n it has
    # no integer solution and the model is infeasible.
    model.addCons(2 * x.sum() == n)

    # The sum of the numbers in A equals the sum of the numbers in B.
    model.addCons((values * x).sum() == (values * (1 - x)).sum())

    # The sum of the squares of the numbers in A equals that of the numbers in B.
    model.addCons((values**2 * x).sum() == (values**2 * (1 - x)).sum())

    # a[k, i] is 1 when the k-th smallest number of A is the number i + 1, and b[k, i]
    # the same for B. Each position holds one number, and each number sits in the list
    # of the set it belongs to. Increasing order makes each set one output, so no two
    # solutions differ only in the order of the numbers.
    a = model.addMatrixVar((half, n), vtype="B", name="a")
    b = model.addMatrixVar((half, n), vtype="B", name="b")
    model.addMatrixCons(a.sum(axis=1) == 1)  # every position of A holds one number
    model.addMatrixCons(b.sum(axis=1) == 1)  # every position of B holds one number
    model.addMatrixCons(a.sum(axis=0) == x)  # a number is placed in A exactly when it is in A
    model.addMatrixCons(b.sum(axis=0) == 1 - x)  # a number is placed in B exactly when it is in B

    A = a @ values  # A[k] is the number at position k of A
    B = b @ values  # B[k] is the number at position k of B
    model.addMatrixCons(A[:-1] + 1 <= A[1:])  # A is increasing
    model.addMatrixCons(B[:-1] + 1 <= B[1:])  # B is increasing

    # A satisfaction problem: no objective is set.
    return model, {"A": A, "B": B}


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
