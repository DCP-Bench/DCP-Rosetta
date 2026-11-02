# heterosquare: a Z3 (Python) model from DCP Rosetta.
# Download the `heterosquare.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/heterosquare.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python heterosquare.py heterosquare.json

import z3


def create_model(instance):
    """A heterosquare of order n is an n by n square of distinct whole numbers from 1 to n^2
    whose row, column and diagonal sums are all different."""
    n = instance["n"]  # the order of the square

    # x[i][j] is the number in row i, column j
    x = [[z3.Int(f"x_{i}_{j}") for j in range(n)] for i in range(n)]

    # The sums of the rows, the columns and the two diagonals
    row_sums = [z3.Int(f"row_sum_{i}") for i in range(n)]
    col_sums = [z3.Int(f"col_sum_{j}") for j in range(n)]
    diag_sum = z3.Int("diag_sum")  # top left to bottom right
    anti_diag_sum = z3.Int("anti_diag_sum")  # top right to bottom left
    all_sums = row_sums + col_sums + [diag_sum, anti_diag_sum]

    solver = z3.Solver()

    # Every number in the square is from 1 to n^2, and each of them is used in exactly one cell.
    solver.add([z3.And(1 <= cell, cell <= n * n) for row in x for cell in row])
    solver.add([z3.PbEq([(cell == v, 1) for row in x for cell in row], 1)
                for v in range(1, n * n + 1)])

    # Each sum adds up its cells.
    solver.add([row_sums[i] == z3.Sum(x[i]) for i in range(n)])
    solver.add([col_sums[j] == z3.Sum([x[i][j] for i in range(n)]) for j in range(n)])
    solver.add(diag_sum == z3.Sum([x[i][i] for i in range(n)]))
    solver.add(anti_diag_sum == z3.Sum([x[i][n - 1 - i] for i in range(n)]))

    # Each sum adds n different numbers from 1 to n^2, so it lies between the sum of the
    # n smallest and the sum of the n largest of them.
    low = n * (n + 1) // 2
    high = n ** 3 - n * (n - 1) // 2
    solver.add([z3.And(low <= s, s <= high) for s in all_sums])

    # All the row, column and diagonal sums are different.
    solver.add(z3.Distinct(all_sums))

    return solver, {"x": x}


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
