# calvin_puzzle: a Z3 (Python) model from DCP Rosetta.
# Download the `calvin_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/calvin_puzzle.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python calvin_puzzle.py calvin_puzzle.json

import z3


def create_model(instance):
    """Fill an n by n grid with the numbers 1 to n^2, each used once, so that every number
    is placed exactly three squares away from the previous one horizontally or vertically,
    or exactly two squares away diagonally."""
    n = instance["n"]  # the grid has n rows and n columns
    cells = n * n      # the number of squares, which is also the largest number

    # The moves from one square to the next: three squares along a row or column, or two
    # squares diagonally.
    moves = [(3, 0), (-3, 0), (0, 3), (0, -3), (2, 2), (2, -2), (-2, 2), (-2, -2)]

    # The squares one move away from square (i, j), staying on the grid.
    def reach(i, j):
        return [(i + di, j + dj) for di, dj in moves if 0 <= i + di < n and 0 <= j + dj < n]

    # x[i][j] is the number written in row i, column j
    x = [[z3.Int(f"x_{i}_{j}") for j in range(n)] for i in range(n)]
    # The numbers in the grid, row by row
    flat = [x[i][j] for i in range(n) for j in range(n)]

    # The rules on the grid.
    solver = z3.Solver()

    # Every square holds a number from 1 to n^2.
    solver.add([z3.And(v >= 1, v <= cells) for v in flat])

    # The numbers are all different, so each number from 1 to n^2 is used exactly once.
    solver.add(z3.Distinct(flat))

    # The next number sits one move away from each square, and the previous number too.
    for i in range(n):
        for j in range(n):
            nearby = [x[a][b] for a, b in reach(i, j)]
            solver.add(z3.Implies(x[i][j] < cells, z3.Or([v == x[i][j] + 1 for v in nearby])))
            solver.add(z3.Implies(x[i][j] > 1, z3.Or([v == x[i][j] - 1 for v in nearby])))

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
