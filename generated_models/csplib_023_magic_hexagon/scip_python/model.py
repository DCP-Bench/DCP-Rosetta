# csplib_023_magic_hexagon: a SCIP (Python) model from DCP Rosetta.
# Download the `csplib_023_magic_hexagon.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_023_magic_hexagon.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python csplib_023_magic_hexagon.py csplib_023_magic_hexagon.json

import numpy as np
from pyscipopt import Model, quicksum

# The layout of the hexagon, cells A to S in the statement's order (A = index 0):
#        A  B  C
#      D  E  F  G
#    H  I  J  K  L
#      M  N  O  P
#        Q  R  S
# The layout is fixed by the statement: the lines use indices 0 to 18, so NUM_CELLS
# must be 19, and the numbers 1 to NUM_CELLS fill exactly these cells.
# LINES are the 15 lines of the statement, as lists of cell indices: the 5 rows,
# then the 5 lines running down-right, then the 5 lines running down-left.
LINES = [
    [0, 1, 2],           # A B C
    [3, 4, 5, 6],        # D E F G
    [7, 8, 9, 10, 11],   # H I J K L
    [12, 13, 14, 15],    # M N O P
    [16, 17, 18],        # Q R S
    [0, 4, 9, 14, 18],   # A E J O S
    [1, 5, 10, 15],      # B F K P
    [2, 6, 11],          # C G L
    [3, 8, 13, 17],      # D I N R
    [7, 12, 16],         # H M Q
    [2, 5, 9, 13, 16],   # C F J N Q
    [1, 4, 8, 12],       # B E I M
    [0, 3, 7],           # A D H
    [6, 10, 14, 17],     # G K O R
    [11, 15, 18],        # L P S
]


def create_model(instance):
    """Magic hexagon: place the numbers 1 to NUM_CELLS, each once, in the cells of a
    hexagon so that every line of cells adds up to MAGIC_SUM. The output LD gives the
    number in each cell, from A to S."""
    num_cells = instance["NUM_CELLS"]  # how many cells there are, and the numbers 1 to num_cells are placed in them
    magic_sum = instance["MAGIC_SUM"]  # the total that every line of cells must reach

    model = Model("magic_hexagon")

    # x[c, v] is 1 when cell c holds the number v + 1, and 0 when not; rows are cells,
    # columns are numbers. SCIP has no all-different constraint, so the numbers are
    # made different with one-hot binaries: each cell takes one number, and each
    # number is in one cell.
    x = model.addMatrixVar((num_cells, num_cells), vtype="B", name="x")

    # numbers[v] is the number v + 1, the value that column v of x stands for.
    numbers = np.arange(1, num_cells + 1)

    # value[c] is the number in cell c: the number v + 1 whose entry x[c, v] is 1.
    value = x @ numbers

    # Each cell holds exactly one number.
    model.addMatrixCons(x.sum(axis=1) == 1)

    # Each number is in exactly one cell. With as many numbers as cells, this and the
    # line above make the cells hold the numbers 1 to num_cells in some order.
    model.addMatrixCons(x.sum(axis=0) == 1)

    # Every line of cells adds up to the magic sum.
    for line in LINES:
        model.addCons(quicksum(value[c] for c in line) == magic_sum)

    # The puzzle asks for an arrangement that works, so there is no objective.
    return model, {"LD": value}


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
