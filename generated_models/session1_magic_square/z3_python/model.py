# session1_magic_square: a Z3 (Python) model from DCP Rosetta.
# Download the `session1_magic_square.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_magic_square.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python session1_magic_square.py session1_magic_square.json

import z3


def create_model(instance):
    """A magic square is an n x n grid in which each cell holds a different
    integer from 1 to n^2 and every row, column and diagonal has the same sum."""
    n = instance["n"]  # the number of rows and columns of the square

    # The common sum is n * (n^2 + 1) / 2: the numbers 1..n^2 total
    # n^2 * (n^2 + 1) / 2, shared equally between n rows.
    magic_sum = n * (n * n + 1) // 2

    # square[i][j] is the number in row i, column j
    square = [[z3.Int(f"square_{i}_{j}") for j in range(n)] for i in range(n)]

    # All cells of the square.
    cells = [cell for row in square for cell in row]

    solver = z3.Solver()

    # Each cell holds a number from 1 to n^2.
    solver.add([bound for cell in cells for bound in (cell >= 1, cell <= n * n)])

    # All numbers in the square are different.
    solver.add(z3.Distinct(cells))

    # Every row adds up to the magic sum.
    solver.add([z3.Sum(row) == magic_sum for row in square])

    # Every column adds up to the magic sum.
    solver.add([z3.Sum([square[i][j] for i in range(n)]) == magic_sum for j in range(n)])

    # The main diagonal adds up to the magic sum.
    solver.add(z3.Sum([square[i][i] for i in range(n)]) == magic_sum)

    # The other diagonal adds up to the magic sum.
    solver.add(z3.Sum([square[i][n - 1 - i] for i in range(n)]) == magic_sum)

    return solver, {"square": square}


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
