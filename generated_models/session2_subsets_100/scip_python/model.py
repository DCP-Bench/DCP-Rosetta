# session2_subsets_100: a SCIP (Python) model from DCP Rosetta.
# Download the `session2_subsets_100.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_subsets_100.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python session2_subsets_100.py session2_subsets_100.json

from pyscipopt import Model
import numpy as np


def create_model(instance):
    """Given a set A of different integers, find two disjoint non-empty
    subsets S and T of A whose elements have the same sum. S and T need not
    use all of A. The outputs say which elements of A are in S (in_S) and
    which are in T (in_T): 1 when the element is in the subset, 0 when not."""
    A = np.array(instance["A"])  # A[i]: the i-th integer of the set A, for i = 0 .. n - 1
    n = len(A)  # the number of integers in A

    model = Model("session2_subsets_100")

    # x is a table with one row per element of A and one column per subset:
    # x[i, 0] is 1 when element i is in S, x[i, 1] is 1 when element i is in T.
    # Binary, so 0 and 1 are the only values: each element is in S or not, and in T or not.
    x = model.addMatrixVar((n, 2), vtype="B", name="x")
    in_S = x[:, 0]  # in_S[i] is 1 when element i of A is in S
    in_T = x[:, 1]  # in_T[i] is 1 when element i of A is in T

    # S and T are disjoint: every element of A is in at most one of them
    model.addMatrixCons(x.sum(axis=1) <= 1)

    # S and T are both non-empty: each column has at least one 1
    model.addMatrixCons(x.sum(axis=0) >= 1)

    # The sum of the elements in S equals the sum of the elements in T
    sums = A @ x  # sums[0] is the sum of S, sums[1] is the sum of T
    model.addCons(sums[0] == sums[1])

    # No objective: the problem only asks for any S and T that meet the conditions
    return model, {"in_S": in_S, "in_T": in_T}


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
