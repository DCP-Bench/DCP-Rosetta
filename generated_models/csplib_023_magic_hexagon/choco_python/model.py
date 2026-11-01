# csplib_023_magic_hexagon: a Choco-solver (Python) model from DCP Rosetta.
# Download the `csplib_023_magic_hexagon.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_023_magic_hexagon.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python csplib_023_magic_hexagon.py csplib_023_magic_hexagon.json

from pychoco.model import Model


def create_model(instance):
    """Place the numbers 1 to n_cells, each once, in the cells of a hexagon (rows of 3, 4, 5, 4 and
    3 cells) so that the numbers along every straight line of cells add up to the magic sum."""
    n_cells = instance["NUM_CELLS"]   # the number of cells, and the largest number placed in them
    magic_sum = instance["MAGIC_SUM"] # the sum that every straight line of cells has to reach

    # The straight lines of cells, with the cells numbered row by row as in this grid:
    #       0  1  2
    #     3  4  5  6
    #   7  8  9 10 11
    #    12 13 14 15
    #      16 17 18
    # They are the 5 rows, the 5 diagonals from top left to bottom right, and the 5 diagonals
    # from top right to bottom left.
    LINES = [
        [0, 1, 2], [3, 4, 5, 6], [7, 8, 9, 10, 11], [12, 13, 14, 15], [16, 17, 18],
        [0, 3, 7], [1, 4, 8, 12], [2, 5, 9, 13, 16], [6, 10, 14, 17], [11, 15, 18],
        [2, 6, 11], [1, 5, 10, 15], [0, 4, 9, 14, 18], [3, 8, 13, 17], [7, 12, 16],
    ]

    model = Model()

    # LD[c] is the number placed in cell c
    LD = [model.intvar(1, n_cells, name=f"LD_{c}") for c in range(n_cells)]

    # Every number from 1 to n_cells is used exactly once.
    model.all_different(LD).post()

    # Every straight line of cells adds up to the magic sum.
    for line in LINES:
        model.sum([LD[c] for c in line], "=", magic_sum).post()

    return model, {"LD": LD}, None


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
