# futoshiki: a Python-MIP (Python) model from DCP Rosetta.
# Download the `futoshiki.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/futoshiki.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python futoshiki.py futoshiki.json

import mip


def create_model(instance):
    """Futoshiki: fill an n-by-n grid with the numbers 1 to n so that every row and column holds each
    number once, the given numbers are in place, and the inequality signs between neighbouring squares hold."""
    values = instance["values"]  # the digits given at the start, by row and column, with 0 for an empty square
    lt = instance["lt"]          # each inequality sign: the smaller square's row and column, then the larger one's, counting from 1
    n = len(values)              # the number of rows, of columns and of numbers

    model = mip.Model(solver_name="CBC")

    # The numbers that fill the grid: 1 to n.
    digits = range(1, n + 1)

    # p[i][j][v] is 1 when the square in row i, column j holds the number v.
    p = [[{v: model.add_var(f"p_{i}_{j}_{v}", var_type=mip.BINARY) for v in digits}
          for j in range(n)] for i in range(n)]
    # grid[i][j] is the number in row i, column j. A given number fixes its square; an empty square can hold any number.
    grid = [[model.add_var(f"grid_{i}_{j}", lb=values[i][j] or 1, ub=values[i][j] or n, var_type=mip.INTEGER)
             for j in range(n)] for i in range(n)]

    # Each square holds exactly one number, and its grid value is that number.
    for i in range(n):
        for j in range(n):
            model += mip.xsum(p[i][j][v] for v in digits) == 1
            model += grid[i][j] == mip.xsum(v * p[i][j][v] for v in digits)

    # Each row holds each number once.
    for i in range(n):
        for v in digits:
            model += mip.xsum(p[i][j][v] for j in range(n)) == 1

    # Each column holds each number once.
    for j in range(n):
        for v in digits:
            model += mip.xsum(p[i][j][v] for i in range(n)) == 1

    # The smaller square of each inequality sign holds a smaller number than the larger square.
    for r1, c1, r2, c2 in lt:
        model += grid[r1 - 1][c1 - 1] + 1 <= grid[r2 - 1][c2 - 1]

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
