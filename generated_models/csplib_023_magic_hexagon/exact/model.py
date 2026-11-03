# csplib_023_magic_hexagon: an Exact (Python) model from DCP Rosetta.
# Download the `csplib_023_magic_hexagon.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_023_magic_hexagon.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python csplib_023_magic_hexagon.py csplib_023_magic_hexagon.json

from exact import Exact


def create_model(instance):
    """Place the numbers 1 to NUM_CELLS, each once, in the cells of a hexagon (rows of 3, 4, 5, 4
    and 3 cells) so that the numbers along each of the 15 straight lines add up to MAGIC_SUM."""
    n_cells = instance["NUM_CELLS"]    # the number of cells in the hexagon, 19 here
    magic_sum = instance["MAGIC_SUM"]  # the total every straight line of cells must reach
    numbers = range(1, n_cells + 1)    # the numbers to place

    # The cells of the hexagon, with their numbers:
    #       0  1  2
    #     3  4  5  6
    #   7  8  9 10 11
    #    12 13 14 15
    #      16 17 18
    # The 15 straight lines of cells: the 5 rows, and the 5 diagonals in each slanting direction.
    LINES = [
        [0, 1, 2], [3, 4, 5, 6], [7, 8, 9, 10, 11], [12, 13, 14, 15], [16, 17, 18],
        [0, 3, 7], [1, 4, 8, 12], [2, 5, 9, 13, 16], [6, 10, 14, 17], [11, 15, 18],
        [2, 6, 11], [1, 5, 10, 15], [0, 4, 9, 14, 18], [3, 8, 13, 17], [7, 12, 16],
    ]

    solver = Exact()

    # Exact identifies its variables by name.
    # LD[c] is the number placed in cell c
    LD = [f"LD_{c}" for c in range(n_cells)]
    # holds[c][v] is 1 when cell c holds the number v, and 0 when not
    holds = [{} for _ in range(n_cells)]
    for c in range(n_cells):
        solver.addVariable(LD[c], 1, n_cells)
        for v in numbers:
            holds[c][v] = f"holds_{c}_{v}"
            solver.addVariable(holds[c][v], 0, 1)
        # Each cell holds exactly one number.
        solver.addConstraint([(1, holds[c][v]) for v in numbers], True, 1, True, 1)
        # The number placed in cell c is the number it holds.
        solver.addConstraint([(v, holds[c][v]) for v in numbers] + [(-1, LD[c])], True, 0, True, 0)

    # Each number from 1 to NUM_CELLS is placed in exactly one cell.
    for v in numbers:
        solver.addConstraint([(1, holds[c][v]) for c in range(n_cells)], True, 1, True, 1)

    # Each straight line of cells adds up to the magic sum.
    for line in LINES:
        solver.addConstraint([(1, LD[c]) for c in line], True, magic_sum, True, magic_sum)

    return solver, {"LD": LD}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
