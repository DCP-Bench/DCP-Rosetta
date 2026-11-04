# calvin_puzzle: a PySAT (Python) model from DCP Rosetta.
# Download the `calvin_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/calvin_puzzle.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python calvin_puzzle.py calvin_puzzle.json

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine

# The moves from one square to the next, as (row change, column change): three squares along a
# row or a column, or two squares along each diagonal.
MOVES = [(3, 0), (-3, 0), (0, 3), (0, -3), (2, 2), (2, -2), (-2, 2), (-2, -2)]


def create_model(instance):
    """Fill an n by n grid with the numbers 1 to n^2 in sequence. The next number goes either
    exactly three squares away horizontally or vertically, or exactly two squares away
    diagonally from the previous one."""
    n = instance["n"]  # the grid has n rows and n columns
    last = n * n       # the largest number in the grid

    pool = IDPool()

    # x[i][j] is the number written in row i, column j
    x = [[Integer(f"x_{i}_{j}", 1, last, vpool=pool) for j in range(n)] for i in range(n)]
    # every square of the grid
    squares = [square for row in x for square in row]
    engine = IntegerEngine(vars=squares, vpool=pool)

    # Each number from 1 to n^2 is written in exactly one square.
    engine.add_alldifferent(squares)
    cnf = engine.clausify()

    for i in range(n):
        for j in range(n):
            # the squares one move away from square (i, j), inside the grid
            reachable = [(i + di, j + dj) for di, dj in MOVES if 0 <= i + di < n and 0 <= j + dj < n]
            # If k is in square (i, j), then k + 1 is in a square one move away.
            for k in range(1, last):
                cnf.append([-x[i][j].equals(k)] + [x[a][b].equals(k + 1) for a, b in reachable])
            # The moves can be reversed: if k + 1 is in square (i, j), then k is in a square one move away.
            for k in range(2, last + 1):
                cnf.append([-x[i][j].equals(k)] + [x[a][b].equals(k - 1) for a, b in reachable])

    return cnf, {"x": x}


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
