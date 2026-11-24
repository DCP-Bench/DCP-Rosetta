# heterosquare: a SCIP (Python) model from DCP Rosetta.
# Download the `heterosquare.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/heterosquare.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python heterosquare.py heterosquare.json

from pyscipopt import Model, quicksum


def create_model(instance):
    """A heterosquare of order n is an n x n square of the integers 1 to n^2,
    each used once, whose row sums, column sums and two diagonal sums are all
    different from one another."""
    n = instance["n"]        # the order of the square (rows and columns)
    cells = n * n            # the square holds the integers 1 to cells, each once

    model = Model("heterosquare")

    # place[v][i, j] is 1 when cell (i, j) holds the integer v + 1, and 0 when not.
    # Each integer is placed exactly once, which makes the square a permutation
    # of 1..n^2 (SCIP has no all-different, so each value gets a placement grid).
    place = [model.addMatrixVar((n, n), vtype="B", name=f"place_{v}")
             for v in range(cells)]

    # x[i, j] is the integer in row i, column j of the square, from 1 to n^2
    # as the statement says.
    x = model.addMatrixVar((n, n), vtype="I", lb=1, ub=cells, name="x")

    # Every cell holds exactly one integer.
    model.addMatrixCons(sum(place) == 1)
    # Every integer 1..n^2 is placed in exactly one cell.
    for grid in place:
        model.addCons(grid.sum() == 1)
    # x takes the integer each placement grid selects.
    model.addMatrixCons(x == sum((v + 1) * place[v] for v in range(cells)))

    # The 2n + 2 sums: n row sums, n column sums, and the two diagonals.
    rows = [quicksum(x[i, j] for j in range(n)) for i in range(n)]
    cols = [quicksum(x[i, j] for i in range(n)) for j in range(n)]
    diag = quicksum(x[i, i] for i in range(n))
    anti = quicksum(x[i, n - 1 - i] for i in range(n))
    sums = rows + cols + [diag, anti]

    # Every pair of sums differs. SCIP has no !=, so each pair gets one binary
    # d that picks the side: d == 1 forces the first sum above the second,
    # d == 0 forces the second above the first.
    for a in range(len(sums)):
        for b in range(a + 1, len(sums)):
            d = model.addVar(vtype="B", name=f"side_{a}_{b}")
            model.addConsIndicator(sums[a] - sums[b] >= 1, binvar=d)
            model.addConsIndicator(sums[b] - sums[a] >= 1, binvar=d, activeone=False)

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
