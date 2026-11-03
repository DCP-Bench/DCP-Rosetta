# csplib_015_schurs_lemma: a SCIP (Python) model from DCP Rosetta.
# Download the `csplib_015_schurs_lemma.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_015_schurs_lemma.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python csplib_015_schurs_lemma.py csplib_015_schurs_lemma.json

from pyscipopt import Model, quicksum


def create_model(instance):
    """Schur's lemma: put the balls labelled 1, ..., n into c boxes so that for
    every triple of balls (x, y, z) with x + y = z, the three balls are not all
    in the same box. The statement says that with 3 boxes a solution exists if
    and only if n < 14. The output balls[i] is the box, from 1 to c, of ball i + 1."""
    n = instance["n"]  # the number of balls, labelled 1 to n
    c = instance["c"]  # the number of boxes (the statement fixes it at 3)

    model = Model("schurs_lemma")

    # M[i, j] is 1 when ball i + 1 is in box j + 1, and 0 when not.
    # Balls are 1-based in the statement and rows are 0-based, so ball v is row v - 1.
    M = model.addMatrixVar((n, c), vtype="B", name="M")

    # Each ball is in exactly one box: the row of each ball sums to 1.
    model.addMatrixCons(M.sum(axis=1) == 1)

    # For each triple x + y = z with x <= y and each box j, at most two of the
    # three balls are in box j, so not all three are. The triples are the
    # statement's: x = y is included, so a ball may pair with itself (1 + 1 = 2).
    # y runs from x to n - x, which keeps z = x + y at most n.
    for x in range(1, n + 1):
        for y in range(x, n - x + 1):
            z = x + y
            for j in range(c):
                model.addCons(M[x - 1, j] + M[y - 1, j] + M[z - 1, j] <= 2)

    # The output is the box of each ball: the one-hot sum of (j + 1) * M[i, j]
    # gives the box number directly, so no extra integer variable is needed.
    balls = [quicksum((j + 1) * M[i, j] for j in range(c)) for i in range(n)]

    return model, {"balls": balls}


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
