# csplib_057_killer_sudoku: a PySAT (Python) model from DCP Rosetta.
# Download the `csplib_057_killer_sudoku.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_057_killer_sudoku.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python csplib_057_killer_sudoku.py csplib_057_killer_sudoku.json

from math import isqrt

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Fill an n-by-n grid with the numbers 1 to n so that every row, column and box
    holds each number once, and every cage (a group of cells) holds distinct numbers
    adding up to the small number printed in its corner."""
    n_side = instance["n"]        # side of the grid, which is also the largest digit
    cages = instance["problem"]   # the cages: the total of each and the cells it covers, counted from 1
    box_side = isqrt(n_side)      # side of a box (3 for the usual 9x9 grid)

    pool = IDPool()

    # x[r][c] is the digit written in the cell at row r, column c, from 1 to n_side.
    x = [[Integer(f"x_{r}_{c}", 1, n_side, vpool=pool) for c in range(n_side)]
         for r in range(n_side)]
    engine = IntegerEngine(vars=[cell for row in x for cell in row], vpool=pool)

    # Every row and every column holds each digit once.
    for i in range(n_side):
        engine.add_alldifferent(x[i])
        engine.add_alldifferent([x[r][i] for r in range(n_side)])
    # Every box holds each digit once.
    for i in range(box_side):
        for j in range(box_side):
            engine.add_alldifferent([x[r][c] for r in range(i * box_side, (i + 1) * box_side)
                                     for c in range(j * box_side, (j + 1) * box_side)])

    # Every cage adds up to its total, and no digit repeats inside it.
    for target, cells in cages:
        # The digits written in the cells of this cage.
        cage = [x[r - 1][c - 1] for r, c in cells]
        engine.add_linear(sum(cage) == target)
        engine.add_alldifferent(cage)

    return engine.clausify(), {"x": x}


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
