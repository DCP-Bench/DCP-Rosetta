# equal_sized_groups: a SCIP (Python) model from DCP Rosetta.
# Download the `equal_sized_groups.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/equal_sized_groups.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python equal_sized_groups.py equal_sized_groups.json

import numpy as np
from pyscipopt import Model, quicksum


def create_model(instance):
    """Cut a sorted list of N elements into K consecutive groups, each as close
    in size as possible to round(N / K), without splitting a run of equal values.
    The total error, the sum over the groups of |size - round(N / K)|, is minimised.
    Each group holds at least one element."""
    a = instance["a"]  # a[i]: the i-th element of the sorted list, counted from 0
    k = instance["k"]  # K: the number of groups
    n = len(a)         # N: the number of elements, read from the list itself

    # round(N / K): the ideal size of a group. Python's round sends an exact half
    # to the even neighbour; the statement does not say which half-way rule to use.
    target = round(n / k)

    model = Model("equal_sized_groups")

    # y[j, p - 1] is 1 when break j is placed after element p (counted from 1), so
    # group j + 1 ends at element p. A break after p is allowed only where the
    # next element has a different value, so equal values stay in one group; the
    # bound 0 on the other entries comes from the data (a[p - 1] == a[p] there).
    allowed = [[int(a[p - 1] != a[p]) for p in range(1, n)] for _ in range(k - 1)]
    y = model.addMatrixVar((k - 1, n - 1), vtype="B", name="y", ub=allowed)

    # Each break point takes exactly one position. The allowed positions are a set
    # picked out of the data, not an interval, so each break point is a one-hot row.
    model.addMatrixCons(y.sum(axis=1) == 1)

    # x[j] is the 1-based index of the last element of group j + 1, that is the
    # position of break point j.
    x = y @ np.arange(1, n)

    # cuts[g] is the number of elements before group g + 1. The first group starts
    # after 0 elements and the last group ends at element N, which are fixed by the
    # problem, so cuts[0] = 0 and cuts[K] = N.
    cuts = [0] + list(x) + [n]

    # err[g] is the error of group g + 1, |size - target|. The sizes are between 0
    # and N and so is the target, so an error is at most N.
    err = [model.addVar(f"err_{g}", vtype="I", lb=0, ub=n) for g in range(k)]

    for g in range(k):
        size = cuts[g + 1] - cuts[g]  # the number of elements in group g + 1

        # err[g] is at least the error of group g + 1 in either direction. Only the
        # lower bounds are posted: the objective minimises the errors, so each one
        # settles at exactly |size - target|.
        model.addCons(err[g] >= size - target)
        model.addCons(err[g] >= target - size)

        # Each group is non-empty, as the statement asks for K groups. This also makes
        # the break points strictly increase, since no two can be at the same place.
        model.addCons(cuts[g] + 1 <= cuts[g + 1])

    # Total error: the sum of the errors of the groups, to be minimised.
    model.setObjective(quicksum(err), "minimize")

    return model, {"x": x}


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
