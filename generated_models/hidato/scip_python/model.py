# hidato: a SCIP (Python) model from DCP Rosetta.
# Download the `hidato.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/hidato.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python hidato.py hidato.json

import numpy as np
from pyscipopt import Model


def create_model(instance):
    """Hidato: fill every empty cell of a grid with a number so that the numbers
    1 to the number of cells each appear once, and each number touches the next
    one (number k and number k + 1) horizontally, vertically or diagonally.
    Some cells already hold a number, which must stay where it is."""
    # puzzle[r, c]: the number given in cell (r, c), or 0 for an empty cell
    puzzle = np.array(instance["puzzle"])
    rows, cols = puzzle.shape
    # the cell count, from the grid's size. Hidato numbers the cells 1 to this count,
    # every cell getting one number and every number used once.
    cells = rows * cols
    # numbers[k] = k + 1: index k of place below stands for the number k + 1
    numbers = np.arange(1, cells + 1)
    # row_index[r, c] = r and col_index[r, c] = c: the position of each cell
    row_index, col_index = np.indices((rows, cols))

    model = Model("hidato")

    # place[k, r, c] is 1 when the number numbers[k] is in cell (r, c), and 0 when not.
    # SCIP has no all-different constraint, so the numbers are placed with one-hot
    # binaries instead: each cell holds one number and each number sits in one cell.
    # The bounds fix the given numbers: a given number is forced to 1 in its own cell
    # (lower bound), and forced to 0 in each cell that holds a different given number
    # (upper bound).
    given = puzzle[None, :, :] == numbers[:, None, None]
    empty = puzzle[None, :, :] == 0
    place = model.addMatrixVar((cells, rows, cols), vtype="B", name="place",
                               lb=given.astype(int).tolist(),
                               ub=(given | empty).astype(int).tolist())

    # Each cell holds exactly one number.
    model.addMatrixCons(place.sum(axis=0) == 1)
    # Each number sits in exactly one cell, so the numbers are all different.
    model.addMatrixCons(place.sum(axis=2).sum(axis=1) == 1)

    # row[k] and col[k]: the row and the column of number numbers[k]. Each is linear
    # in place, because exactly one cell holds that number.
    row = (place * row_index).sum(axis=2).sum(axis=1)
    col = (place * col_index).sum(axis=2).sum(axis=1)

    # Consecutive numbers touch. Two cells touch horizontally, vertically or diagonally
    # exactly when their rows differ by at most 1 and their columns differ by at most 1,
    # so each pair of consecutive numbers gets these four linear constraints.
    row_step = row[1:] - row[:-1]
    col_step = col[1:] - col[:-1]
    model.addMatrixCons(row_step <= 1)
    model.addMatrixCons(row_step >= -1)
    model.addMatrixCons(col_step <= 1)
    model.addMatrixCons(col_step >= -1)

    # x[r, c]: the number in cell (r, c), the number times its placement, summed over numbers
    x = (place * numbers[:, None, None]).sum(axis=0)

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
