# csplib_023_magic_hexagon: a Python-MIP (Python) model from DCP Rosetta.
# Download the `csplib_023_magic_hexagon.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_023_magic_hexagon.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python csplib_023_magic_hexagon.py csplib_023_magic_hexagon.json

import mip


def create_model(instance):
    """Place the numbers 1 to NUM_CELLS, each once, in the 19 cells of a hexagon so that the
    numbers in each of the 15 lines of cells (rows and diagonals) add up to MAGIC_SUM."""
    n_numbers = instance["NUM_CELLS"]  # the numbers to place: 1 up to n_numbers
    magic_sum = instance["MAGIC_SUM"]  # the total every line of cells has to reach
    n_cells = 19  # the hexagon has 19 cells, in rows of 3, 4, 5, 4 and 3

    # The cells of the hexagon, numbered from the top row down:
    #       0  1  2
    #     3  4  5  6
    #   7  8  9 10 11
    #    12 13 14 15
    #      16 17 18
    LINES = [
        # the five rows
        [0, 1, 2],
        [3, 4, 5, 6],
        [7, 8, 9, 10, 11],
        [12, 13, 14, 15],
        [16, 17, 18],
        # the five diagonals running down to the right
        [0, 4, 9, 14, 18],
        [1, 5, 10, 15],
        [2, 6, 11],
        [3, 8, 13, 17],
        [7, 12, 16],
        # the five diagonals running down to the left
        [2, 5, 9, 13, 16],
        [1, 4, 8, 12],
        [0, 3, 7],
        [6, 10, 14, 17],
        [11, 15, 18],
    ]

    model = mip.Model(solver_name="CBC")
    # The question asks for one arrangement, so the search looks for a valid one first.
    model.emphasis = 1

    # The number written in each cell, from 1 to n_numbers
    cell = [model.add_var(f"cell_{i}", lb=1, ub=n_numbers, var_type=mip.INTEGER) for i in range(n_cells)]

    # All numbers in the cells are different. For each pair of cells, a choice (1 or 0) says which
    # of the two cells holds the larger number, and the two constraints below order the pair.
    for i in range(n_cells):
        for j in range(i + 1, n_cells):
            first_larger = model.add_var(f"larger_{i}_{j}", var_type=mip.BINARY)
            # If cell i holds the larger number, it is at least one more than cell j.
            model += cell[i] - cell[j] >= 1 - n_numbers * (1 - first_larger)
            # Otherwise cell j is at least one more than cell i.
            model += cell[j] - cell[i] >= 1 - n_numbers * first_larger

    # Every line of cells adds up to the magic sum.
    for line in LINES:
        model += mip.xsum(cell[i] for i in line) == magic_sum

    return model, {"LD": cell}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
