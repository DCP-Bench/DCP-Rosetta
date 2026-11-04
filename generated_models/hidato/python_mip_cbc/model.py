# hidato: a Python-MIP (Python) model from DCP Rosetta.
# Download the `hidato.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/hidato.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python hidato.py hidato.json

import mip

# The eight steps from a cell to the cells that touch it.
OFFSETS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


def neighbours(i, j, rows, cols):
    """The cells that touch cell (i, j) horizontally, vertically or diagonally."""
    for di, dj in OFFSETS:
        a, b = i + di, j + dj
        if 0 <= a < rows and 0 <= b < cols:
            yield a, b


def create_model(instance):
    """A Hidato puzzle: fill the grid with the numbers 1 to rows * columns, each used once,
    keeping the numbers already on the board, so that each number touches the next one
    horizontally, vertically or diagonally."""
    puzzle = instance["puzzle"]  # the grid as given, with 0 for an empty cell
    n_rows = len(puzzle)  # the grid has this many rows
    n_cols = len(puzzle[0])  # and this many columns
    n_cells = n_rows * n_cols  # the numbers to place are 1 to n_cells

    model = mip.Model(solver_name="CBC")

    # p[i][j][k] is 1 when cell (i, j) holds the number k + 1. A number on the board fixes its cell.
    p = [[[model.add_var(f"p_{i}_{j}_{k}", var_type=mip.BINARY,
                         lb=1 if puzzle[i][j] == k + 1 else 0)
           for k in range(n_cells)]
          for j in range(n_cols)]
         for i in range(n_rows)]
    # x[i][j] is the number in cell (i, j)
    x = [[model.add_var(f"x_{i}_{j}", lb=1, ub=n_cells, var_type=mip.INTEGER)
          for j in range(n_cols)] for i in range(n_rows)]

    # Each cell holds exactly one number, and x is that number.
    for i in range(n_rows):
        for j in range(n_cols):
            model += mip.xsum(p[i][j]) == 1
            model += x[i][j] == mip.xsum((k + 1) * p[i][j][k] for k in range(n_cells))

    # Each number from 1 to n_cells is in exactly one cell.
    for k in range(n_cells):
        model += mip.xsum(p[i][j][k] for i in range(n_rows) for j in range(n_cols)) == 1

    # Each number is followed by the next one, in a cell that touches it.
    for k in range(n_cells - 1):
        for i in range(n_rows):
            for j in range(n_cols):
                touching = mip.xsum(p[a][b][k + 1] for a, b in neighbours(i, j, n_rows, n_cols))
                model += p[i][j][k] <= touching

    return model, {"x": x}


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
