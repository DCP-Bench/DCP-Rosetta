# csplib_023_magic_hexagon: a Z3 (Python) model from DCP Rosetta.
# Download the `csplib_023_magic_hexagon.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_023_magic_hexagon.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python csplib_023_magic_hexagon.py csplib_023_magic_hexagon.json

import z3


def create_model(instance):
    """Place the numbers 1 to NUM_CELLS, each once, in the cells of a hexagon (rows of 3, 4, 5, 4
    and 3 cells for 19 cells) so that every straight line of cells adds up to MAGIC_SUM."""
    n_cells = instance["NUM_CELLS"]    # the number of cells in the hexagon, 19 here
    magic_sum = instance["MAGIC_SUM"]  # the sum that every straight line of cells has to reach

    # The straight lines of cells, with the cells of the hexagon labelled row by row from the top:
    #       0  1  2
    #     3  4  5  6
    #   7  8  9 10 11
    #    12 13 14 15
    #      16 17 18
    lines = [
        # the 5 horizontal rows
        [0, 1, 2], [3, 4, 5, 6], [7, 8, 9, 10, 11], [12, 13, 14, 15], [16, 17, 18],
        # the 5 diagonals from top left to bottom right
        [0, 3, 7], [1, 4, 8, 12], [2, 5, 9, 13, 16], [6, 10, 14, 17], [11, 15, 18],
        # the 5 diagonals from top right to bottom left
        [2, 6, 11], [1, 5, 10, 15], [0, 4, 9, 14, 18], [3, 8, 13, 17], [7, 12, 16],
    ]

    # The number written in each cell
    LD = [z3.Int(f"LD_{c}") for c in range(n_cells)]

    solver = z3.Solver()

    # Each cell holds a number from 1 to n_cells.
    solver.add([z3.And(cell >= 1, cell <= n_cells) for cell in LD])

    # Each number from 1 to n_cells is written in exactly one cell.
    solver.add(z3.Distinct(LD))

    # Every straight line of cells adds up to the magic sum.
    solver.add([z3.Sum([LD[c] for c in line]) == magic_sum for line in lines])

    return solver, {"LD": LD}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
