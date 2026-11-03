# csplib_003_quasigroup_existence: a SCIP (Python) model from DCP Rosetta.
# Download the `csplib_003_quasigroup_existence.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_003_quasigroup_existence.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python csplib_003_quasigroup_existence.py csplib_003_quasigroup_existence.json

from pyscipopt import Model
import numpy as np


def create_model(instance):
    """Find a quasigroup of order m: an m x m multiplication table with the elements
    0 to m-1, in which every element occurs exactly once in each row and each column,
    and in which (a*b)*(b*a) = a holds for all a and b (the QG3 condition)."""
    m = instance["m"]  # the order m (instance field m): the table is m x m, with elements 0 to m-1

    model = Model("csplib_003_quasigroup_existence")

    # x[a, b, c] is 1 when the table entry in row a, column b is c (a*b = c), and 0 otherwise.
    # PySCIPOpt has no all-different constraint, so the permutation conditions below are
    # written over one-hot binaries: each entry gets one binary per element c, and exactly
    # one of them is 1. The elements are 0 to m-1 by the statement, which gives the size m
    # of the last axis.
    x = model.addMatrixVar((m, m, m), vtype="B", name="x")

    # Every entry of the table holds exactly one element: for each row a and column b,
    # exactly one c has x[a, b, c] = 1.
    model.addMatrixCons(x.sum(axis=2) == 1)

    # Every row is a permutation: element c occurs exactly once in row a, so for each a
    # and c exactly one column b has x[a, b, c] = 1.
    model.addMatrixCons(x.sum(axis=1) == 1)

    # Every column is a permutation: element c occurs exactly once in column b, so for
    # each b and c exactly one row a has x[a, b, c] = 1.
    model.addMatrixCons(x.sum(axis=0) == 1)

    # QG3: (a*b)*(b*a) = a. For a table, let p = a*b and q = b*a; then x[a, b, p] = 1 and
    # x[b, a, q] = 1. The condition then says p*q = a, that is x[p, q, a] = 1. Each entry holds exactly one
    # element, so for given a and b only one p and one q have their binary equal to 1; the
    # implication for every quadruple (a, b, p, q) therefore says exactly that (a*b)*(b*a) = a.
    # The implication is linear in the binaries: x[a, b, p] + x[b, a, q] <= 1 + x[p, q, a]
    # is violated only when the first two are 1 and the third is 0. One constraint per
    # quadruple, m**4 in all.
    for a in range(m):
        for b in range(m):
            for p in range(m):
                for q in range(m):
                    model.addCons(x[a, b, p] + x[b, a, q] <= 1 + x[p, q, a])

    # The table: entry [a][b] is the element c of the one x[a, b, c] that is 1, that is the
    # sum of c * x[a, b, c] over c. The one-hot constraints make this sum a single element.
    table = (x * np.arange(m)).sum(axis=2)

    # The problem asks for a table only: there is no objective, so any table meeting the
    # constraints above is a solution.
    return model, {"quasigroup": table}


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
