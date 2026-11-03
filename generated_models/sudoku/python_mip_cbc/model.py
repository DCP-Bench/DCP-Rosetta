# sudoku: a Python-MIP (Python) model from DCP Rosetta.
# Download the `sudoku.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/sudoku.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python sudoku.py sudoku.json

import math

import mip


def create_model(instance):
    """Sudoku: fill a 9 x 9 grid with the digits 1 to 9 so that every row, every
    column and every 3 x 3 block holds each digit exactly once, keeping the digits
    already given."""
    givens = instance["input_grid"]  # givens[i][j] is the digit given in row i, column j, or 0 when the cell is empty
    n = len(givens)                  # the side of the grid
    box = math.isqrt(n)              # the side of a block
    digits = range(1, n + 1)         # the digits to place

    model = mip.Model(solver_name="CBC")

    # x[i][j][v - 1] is 1 when cell (i, j) holds the digit v, and 0 when not.
    x = [
        [[model.add_var(f"x_{i}_{j}_{v}", var_type=mip.BINARY) for v in digits] for j in range(n)]
        for i in range(n)
    ]
    # grid[i][j] is the digit in cell (i, j).
    grid = [
        [model.add_var(f"g_{i}_{j}", lb=1, ub=n, var_type=mip.INTEGER) for j in range(n)]
        for i in range(n)
    ]

    # Each cell holds exactly one digit, and its grid value is that digit.
    for i in range(n):
        for j in range(n):
            model.add_constr(mip.xsum(x[i][j][k] for k in range(n)) == 1)
            model.add_constr(grid[i][j] == mip.xsum(v * x[i][j][v - 1] for v in digits))

    # The given digits stay in their cells.
    for i in range(n):
        for j in range(n):
            if givens[i][j] != 0:
                model.add_constr(x[i][j][givens[i][j] - 1] == 1)

    # Each row holds every digit once.
    for i in range(n):
        for v in digits:
            model.add_constr(mip.xsum(x[i][j][v - 1] for j in range(n)) == 1)

    # Each column holds every digit once.
    for j in range(n):
        for v in digits:
            model.add_constr(mip.xsum(x[i][j][v - 1] for i in range(n)) == 1)

    # Each box x box block holds every digit once.
    for bi in range(0, n, box):
        for bj in range(0, n, box):
            for v in digits:
                model.add_constr(
                    mip.xsum(
                        x[i][j][v - 1]
                        for i in range(bi, bi + box)
                        for j in range(bj, bj + box)
                    )
                    == 1
                )

    return model, {"grid": grid}


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
