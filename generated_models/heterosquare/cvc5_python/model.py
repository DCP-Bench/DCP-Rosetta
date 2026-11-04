# heterosquare: a cvc5 (Python) model from DCP Rosetta.
# Download the `heterosquare.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/heterosquare.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python heterosquare.py heterosquare.json

import cvc5.pythonic as c5


def create_model(instance):
    """A heterosquare of order n is an n by n square of distinct whole numbers from 1 to n^2
    whose row, column and diagonal sums are all different."""
    n = instance["n"]  # the order of the square
    n_cells = n * n  # how many cells the square has, and the largest number in it
    cell_total = n_cells * (n_cells + 1) // 2  # the sum of the numbers 1 to n^2

    # A row, column or diagonal holds n different numbers from 1 to n^2, so its sum lies
    # between the sum of 1 to n and the sum of the n largest numbers.
    line_min = n * (n + 1) // 2
    line_max = n * (2 * n_cells - n + 1) // 2

    # x[i][j] is the number in row i, column j
    x = [[c5.Int(f"x_{i}_{j}") for j in range(n)] for i in range(n)]

    # All the numbers of the square, row by row.
    cells = [x[i][j] for i in range(n) for j in range(n)]

    solver = c5.Solver()

    # Each number is between 1 and n^2.
    solver.add([c5.And(c >= 1, c <= n_cells) for c in cells])

    # The numbers in the square are all different.
    solver.add(c5.Distinct(cells))

    # The numbers add up to the total of 1 to n^2.
    solver.add(c5.Sum(cells) == cell_total)

    # The sum of each row.
    row_sums = [c5.Sum(x[i]) for i in range(n)]

    # The sum of each column.
    col_sums = [c5.Sum([x[i][j] for i in range(n)]) for j in range(n)]

    # The sums of the two diagonals, from top left to bottom right and from top right to bottom left.
    diag_sums = [
        c5.Sum([x[i][i] for i in range(n)]),
        c5.Sum([x[i][n - 1 - i] for i in range(n)]),
    ]

    # Every row, column and diagonal sum.
    all_sums = row_sums + col_sums + diag_sums

    # Each sum lies between line_min and line_max.
    solver.add([c5.And(s >= line_min, s <= line_max) for s in all_sums])

    # All the row, column and diagonal sums are different.
    solver.add(c5.Distinct(all_sums))

    return solver, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
