# csplib_057_killer_sudoku: a Python-MIP (Python) model from DCP Rosetta.
# Download the `csplib_057_killer_sudoku.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_057_killer_sudoku.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python csplib_057_killer_sudoku.py csplib_057_killer_sudoku.json

import math

import mip


def create_model(instance):
    """Fill an n-by-n grid with the numbers 1 to n so that every row, column and nonet
    holds each number once, and every cage (a group of cells) holds distinct numbers
    adding up to the small number printed in its corner."""
    n = instance["n"]            # the grid is n by n, with numbers 1 to n
    cages = instance["problem"]  # cages[k] is [total, cells]: the total printed in the corner of cage k, and its cells
    block = math.isqrt(n)        # the side of a nonet (3 for the usual 9 by 9 grid)
    digits = range(1, n + 1)     # the numbers 1 to n

    model = mip.Model(solver_name="CBC")

    # p[r, c, v] is 1 when cell (r, c) holds the number v, and 0 when not
    p = {}
    for r in range(n):
        for c in range(n):
            for v in digits:
                p[r, c, v] = model.add_var(f"p_{r}_{c}_{v}", var_type=mip.BINARY)

    # x[r][c] is the number in the cell at row r, column c
    x = [[model.add_var(f"x_{r}_{c}", lb=1, ub=n, var_type=mip.INTEGER)
          for c in range(n)]
         for r in range(n)]

    # Each cell holds exactly one number, and x[r][c] is that number.
    for r in range(n):
        for c in range(n):
            model += mip.xsum(p[r, c, v] for v in digits) == 1
            model += x[r][c] == mip.xsum(v * p[r, c, v] for v in digits)

    # units[u] lists the cells of one row, column or nonet.
    units = []
    for r in range(n):
        units.append([(r, c) for c in range(n)])
    for c in range(n):
        units.append([(r, c) for r in range(n)])
    for br in range(0, n, block):
        for bc in range(0, n, block):
            units.append([(br + i, bc + j) for i in range(block) for j in range(block)])

    # Each row, column and nonet holds each number exactly once.
    for unit in units:
        for v in digits:
            model += mip.xsum(p[r, c, v] for (r, c) in unit) == 1

    # The cells of each cage, counted from 1 as in the puzzle, add up to its total,
    # and no number repeats within a cage.
    for total, cells in cages:
        cell_list = [(r - 1, c - 1) for r, c in cells]
        model += mip.xsum(x[r][c] for (r, c) in cell_list) == total
        for v in digits:
            model += mip.xsum(p[r, c, v] for (r, c) in cell_list) <= 1

    grid = [[x[r][c] for c in range(n)] for r in range(n)]
    return model, {"x": grid}


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
