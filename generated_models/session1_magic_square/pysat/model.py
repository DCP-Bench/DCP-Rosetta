# session1_magic_square: a PySAT (Python) model from DCP Rosetta.
# Download the `session1_magic_square.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_magic_square.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python session1_magic_square.py session1_magic_square.json

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Fill an n x n grid with the different whole numbers 1 to n^2 so that every
    row, every column and both diagonals add up to the same sum."""
    n = instance["n"]  # the number of rows and columns of the square

    # The sum every row, column and diagonal has to reach: the numbers 1 to n^2 added up,
    # shared equally by the n rows.
    magic_sum = n * (n * n + 1) // 2

    pool = IDPool()
    # square[i][j] is the number in row i, column j, from 1 to n^2
    square = [[Integer(f"square_{i}_{j}", 1, n * n, vpool=pool) for j in range(n)] for i in range(n)]
    # Every cell of the square, in one list
    cells = [cell for row in square for cell in row]
    engine = IntegerEngine(vars=cells, vpool=pool)

    # The only cell of a 1 x 1 square holds 1, which its range already gives.
    if n > 1:
        # All numbers in the square are different.
        engine.add_alldifferent(cells)

        # Every row and every column adds up to the magic sum.
        for i in range(n):
            engine.add_linear(sum(square[i][j] for j in range(n)) == magic_sum)
            engine.add_linear(sum(square[j][i] for j in range(n)) == magic_sum)

        # Both diagonals add up to the magic sum.
        engine.add_linear(sum(square[i][i] for i in range(n)) == magic_sum)
        engine.add_linear(sum(square[i][n - 1 - i] for i in range(n)) == magic_sum)

    return engine.clausify(), {"square": square}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.solvers import Solver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
