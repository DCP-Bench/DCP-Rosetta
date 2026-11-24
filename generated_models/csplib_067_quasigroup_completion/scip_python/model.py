# csplib_067_quasigroup_completion: a SCIP (Python) model from DCP Rosetta.
# Download the `csplib_067_quasigroup_completion.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_067_quasigroup_completion.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python csplib_067_quasigroup_completion.py csplib_067_quasigroup_completion.json

from pyscipopt import Model
import numpy as np


def create_model(instance):
    """An order N quasigroup (a Latin square) is an N x N table in which each of
    the values 1..N occurs exactly once in every row and every column. Some cells
    of the table are already filled in: complete it by filling in the empty cells."""
    N = instance["N"]          # the order: the table is N x N and holds the values 1..N
    start = instance["start"]  # start[r][c]: the value given in cell (r, c), or 0 when the cell is empty

    model = Model("csplib_067_quasigroup_completion")

    # x[r, c, v] is 1 when cell (r, c) holds the value v + 1, and 0 when not.
    # Binaries are one-hot because SCIP has no all-different constraint: "each value
    # once per row or column" is then a sum over these binaries.
    # The bounds encode the given cells: a cell with a given value gets lb = 1 on that
    # value and ub = 0 on the others; an empty cell (0 in the data) keeps ub = 1 on all.
    # The bounds come from the instance's start field and the values 1..N of the statement.
    lb = [[[1 if start[r][c] == v + 1 else 0 for v in range(N)]
           for c in range(N)] for r in range(N)]
    ub = [[[1 if start[r][c] in (0, v + 1) else 0 for v in range(N)]
           for c in range(N)] for r in range(N)]
    x = model.addMatrixVar((N, N, N), vtype="B", lb=lb, ub=ub, name="x")

    # Each cell holds exactly one value: for every cell, its N binaries sum to 1.
    model.addMatrixCons(x.sum(axis=2) == 1)
    # Each value occurs exactly once in every row: for every row and value, the
    # binaries over the columns sum to 1.
    model.addMatrixCons(x.sum(axis=1) == 1)
    # Each value occurs exactly once in every column: for every column and value, the
    # binaries over the rows sum to 1.
    model.addMatrixCons(x.sum(axis=0) == 1)

    # puzzle[r][c] is the value of cell (r, c): the value v + 1 whose binary is 1.
    # The sum over v is the output itself, so no separate integer variable is needed.
    values = np.arange(1, N + 1)
    puzzle = (x * values).sum(axis=2)

    return model, {"puzzle": puzzle}


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
