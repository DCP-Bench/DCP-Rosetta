# csplib_076_costas_arrays: a SCIP (Python) model from DCP Rosetta.
# Download the `csplib_076_costas_arrays.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_076_costas_arrays.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python csplib_076_costas_arrays.py csplib_076_costas_arrays.json

import numpy as np
from pyscipopt import Model


def create_model(instance):
    """A Costas array of size n: a permutation costas[0..n-1] of 1..n such that,
    for every gap l = 1..n-1, the differences costas[i + l] - costas[i] are all
    different. The grid has n rows and n columns, with one mark per row and column."""
    n = instance["n"]  # the side of the grid, which is also the number of marks

    model = Model("costas_array")

    # x[i, j] is 1 when the mark in row i sits in column j + 1.
    # SCIP has no all-different constraint, so the permutation is written as one-hot
    # binaries: each row and each column holds exactly one mark.
    x = model.addMatrixVar((n, n), vtype="B", name="x")
    model.addMatrixCons(x.sum(axis=1) == 1)  # one mark in each row
    model.addMatrixCons(x.sum(axis=0) == 1)  # one mark in each column

    # costas[i] is the column (1..n) of the mark in row i. It is an expression over the
    # binaries, so the output needs no integer variable of its own.
    costas = x @ np.arange(1, n + 1)

    # Difference triangle. Every entry of costas is a column from 1 to n, so any two
    # entries differ by at most n - 1 in absolute value. This bound is derived here, not
    # assumed. values[c] = c - (n - 1) is the difference that column c of d stands for.
    values = np.arange(-(n - 1), n)

    for gap in range(1, n):
        # d[i, c] is 1 when costas[i + gap] - costas[i] equals values[c].
        # The all-different constraint of this line is written as "each value is used at
        # most once", the one-hot form SCIP needs for it.
        d = model.addMatrixVar((n - gap, 2 * n - 1), vtype="B", name=f"d{gap}")
        model.addMatrixCons(d.sum(axis=1) == 1)  # each difference of this gap takes one value
        model.addMatrixCons(d.sum(axis=0) <= 1)  # no value is repeated in this line
        model.addMatrixCons(d @ values == costas[gap:] - costas[: n - gap])  # the chosen value is the difference

    return model, {"costas": costas}


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
