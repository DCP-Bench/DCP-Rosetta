# session1_magic_square: a Python-MIP (Python) model from DCP Rosetta.
# Download the `session1_magic_square.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_magic_square.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python session1_magic_square.py session1_magic_square.json

import mip


def create_model(instance):
    """Fill an n x n grid with the numbers 1 to n^2, each used once, so that every
    row, every column and both diagonals add up to the same sum."""
    n = instance["n"]  # the number of rows, and of columns

    cells = [(i, j) for i in range(n) for j in range(n)]  # the cells of the grid, as (row, column)
    values = range(1, n * n + 1)  # the numbers to place
    # The common sum. The numbers 1 to n^2 add up to n^2 (n^2 + 1) / 2, shared equally by the n rows.
    magic_sum = n * (n * n + 1) // 2

    model = mip.Model(solver_name="CBC")

    # square[i][j] is the number in row i, column j.
    square = [[model.add_var(f"sq_{i}_{j}", lb=1, ub=n * n, var_type=mip.INTEGER) for j in range(n)]
              for i in range(n)]

    # p[i, j, v] is 1 when cell (i, j) holds the number v, and 0 when not.
    p = {(i, j, v): model.add_var(f"p_{i}_{j}_{v}", var_type=mip.BINARY)
         for (i, j) in cells for v in values}

    # Each cell holds exactly one number, and that number is square[i][j].
    for (i, j) in cells:
        model += mip.xsum(p[i, j, v] for v in values) == 1
        model += square[i][j] == mip.xsum(v * p[i, j, v] for v in values)

    # Each number from 1 to n^2 is in exactly one cell.
    for v in values:
        model += mip.xsum(p[i, j, v] for (i, j) in cells) == 1

    # Every row adds up to the magic sum.
    for i in range(n):
        model += mip.xsum(square[i][j] for j in range(n)) == magic_sum

    # Every column adds up to the magic sum.
    for j in range(n):
        model += mip.xsum(square[i][j] for i in range(n)) == magic_sum

    # The main diagonal adds up to the magic sum.
    model += mip.xsum(square[i][i] for i in range(n)) == magic_sum

    # The other diagonal adds up to the magic sum.
    model += mip.xsum(square[i][n - 1 - i] for i in range(n)) == magic_sum

    # No objective: any filling that meets the rules answers the puzzle.
    return model, {"square": square}


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
