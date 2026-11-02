# sudoku: a PySAT (Python) model from DCP Rosetta.
# Download the `sudoku.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/sudoku.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python sudoku.py sudoku.json

from math import isqrt

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Fill a 9 x 9 grid with the digits 1 to 9 so that every row, every column and every
    3 x 3 box holds each digit once, keeping the digits already given."""
    given = instance["input_grid"]  # given[r][c] is the digit in row r, column c, or 0 when the cell is empty
    n_side = len(given)             # the side of the grid, which is also the number of digits
    box = isqrt(n_side)             # the side of a box

    pool = IDPool()
    # grid[r][c] is the digit in row r, column c
    grid = [[Integer(f"grid_{r}_{c}", 1, n_side, vpool=pool) for c in range(n_side)]
            for r in range(n_side)]
    engine = IntegerEngine(vars=[cell for row in grid for cell in row], vpool=pool)

    # The given digits stay where they are.
    for r in range(n_side):
        for c in range(n_side):
            if given[r][c] != 0:
                engine.add_linear(grid[r][c] == given[r][c])

    # Each row and each column holds each digit once.
    for i in range(n_side):
        engine.add_alldifferent(grid[i])
        engine.add_alldifferent([grid[r][i] for r in range(n_side)])

    # Each box holds each digit once.
    for i in range(0, n_side, box):
        for j in range(0, n_side, box):
            engine.add_alldifferent([grid[r][c] for r in range(i, i + box) for c in range(j, j + box)])

    return engine.clausify(), {"grid": grid}


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
