# heterosquare: a Python-MIP (Python) model from DCP Rosetta.
# Download the `heterosquare.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/heterosquare.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python heterosquare.py heterosquare.json

import mip


def create_model(instance):
    """A heterosquare of order n is an n by n square of distinct integers from 1 to n^2
    whose row, column and diagonal sums are all different."""
    n_side = instance["n"]  # the order n: the square has n rows and n columns
    n_cells = n_side * n_side  # the numbers in the square are 1 to n_cells

    model = mip.Model(solver_name="CBC")

    # x[i][j] is the number in row i, column j
    x = [[model.add_var(f"x_{i}_{j}", lb=1, ub=n_cells, var_type=mip.INTEGER)
          for j in range(n_side)] for i in range(n_side)]
    # p[i][j][v] is 1 when cell (i, j) holds the number v + 1
    p = [[[model.add_var(f"p_{i}_{j}_{v}", var_type=mip.BINARY)
           for v in range(n_cells)] for j in range(n_side)] for i in range(n_side)]

    # Each cell holds exactly one number, and x is that number.
    for i in range(n_side):
        for j in range(n_side):
            model += mip.xsum(p[i][j]) == 1
            model += x[i][j] == mip.xsum((v + 1) * p[i][j][v] for v in range(n_cells))

    # Each number from 1 to n_cells is in exactly one cell.
    for v in range(n_cells):
        model += mip.xsum(p[i][j][v] for i in range(n_side) for j in range(n_side)) == 1

    # The sums of the rows, the columns and the two diagonals.
    sums = []
    for i in range(n_side):
        sums.append(mip.xsum(x[i][j] for j in range(n_side)))
    for j in range(n_side):
        sums.append(mip.xsum(x[i][j] for i in range(n_side)))
    sums.append(mip.xsum(x[i][i] for i in range(n_side)))
    sums.append(mip.xsum(x[i][n_side - 1 - i] for i in range(n_side)))

    # Any n_side distinct numbers from 1 to n_cells add up to a value between lo and hi.
    lo = n_side * (n_side + 1) // 2
    hi = n_side * n_cells - n_side * (n_side - 1) // 2
    # big is more than the largest possible difference between two such sums.
    big = hi - lo + 1

    # Every two sums differ. a_larger is 1 when sum a is larger than sum c, and 0 when it is smaller.
    for a in range(len(sums)):
        for c in range(a + 1, len(sums)):
            a_larger = model.add_var(f"a_larger_{a}_{c}", var_type=mip.BINARY)
            model += sums[a] - sums[c] <= -1 + big * a_larger
            model += sums[a] - sums[c] >= 1 - big * (1 - a_larger)

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
