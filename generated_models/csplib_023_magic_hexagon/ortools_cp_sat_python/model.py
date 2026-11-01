# csplib_023_magic_hexagon: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `csplib_023_magic_hexagon.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_023_magic_hexagon.html
# Then run it on the first instance (after `pip install ortools`):
#   python csplib_023_magic_hexagon.py csplib_023_magic_hexagon.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Place the numbers 1 to NUM_CELLS, each once, in the cells of a hexagon (rows of 3, 4, 5, 4
    and 3 cells for 19 cells) so that every straight line of cells (rows and both diagonal
    directions) sums to the magic constant."""
    num_cells = instance["NUM_CELLS"]  # the number of cells of the hexagon, 19 here
    magic_sum = instance["MAGIC_SUM"]  # the sum every straight line of cells has to reach

    # The hexagon with the number of each cell:
    #       0  1  2
    #     3  4  5  6
    #   7  8  9 10 11
    #    12 13 14 15
    #      16 17 18
    # Every straight line of cells:
    lines = [
        # the 5 horizontal rows
        [0, 1, 2], [3, 4, 5, 6], [7, 8, 9, 10, 11], [12, 13, 14, 15], [16, 17, 18],
        # the 5 diagonals running from top left to bottom right
        [0, 3, 7], [1, 4, 8, 12], [2, 5, 9, 13, 16], [6, 10, 14, 17], [11, 15, 18],
        # the 5 diagonals running from top right to bottom left
        [2, 6, 11], [1, 5, 10, 15], [0, 4, 9, 14, 18], [3, 8, 13, 17], [7, 12, 16],
    ]

    model = cp_model.CpModel()

    # LD[c] is the number placed in cell c
    LD = [model.new_int_var(1, num_cells, f"LD_{c}") for c in range(num_cells)]

    # Every number from 1 to NUM_CELLS is used exactly once.
    model.add_all_different(LD)

    # The numbers along each straight line of cells add up to the magic constant.
    for line in lines:
        model.add(sum(LD[c] for c in line) == magic_sum)

    return model, {"LD": LD}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
