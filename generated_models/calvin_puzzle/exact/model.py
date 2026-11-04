# calvin_puzzle: an Exact (Python) model from DCP Rosetta.
# Download the `calvin_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/calvin_puzzle.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python calvin_puzzle.py calvin_puzzle.json

from exact import Exact


def create_model(instance):
    """Fill an n by n grid with the numbers 1 to n^2 in sequence. The next number goes either
    exactly three squares away horizontally or vertically, or exactly two squares away
    diagonally from the previous one."""
    n = instance["n"]  # the grid has n rows and n columns
    n_cells = n * n    # the number of squares, which is also the largest number

    # The steps from one square to the next: three squares along a row or column, or two
    # squares along both axes.
    moves = [(3, 0), (-3, 0), (0, 3), (0, -3), (2, 2), (2, -2), (-2, 2), (-2, -2)]

    def reachable(c):
        # the squares one allowed step from square c; squares are numbered row by row from 0
        i, j = divmod(c, n)
        return [(i + a) * n + (j + b) for a, b in moves
                if 0 <= i + a < n and 0 <= j + b < n]

    solver = Exact()

    # Exact identifies its variables by name.
    # x[i][j] is the number written in row i, column j
    x = [[f"x_{i}_{j}" for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(n):
            solver.addVariable(x[i][j], 1, n_cells)

    # at[k][c] is 1 when the number k + 1 is written in square c, and 0 when not
    at = [[f"at_{k}_{c}" for c in range(n_cells)] for k in range(n_cells)]
    for k in range(n_cells):
        for c in range(n_cells):
            solver.addVariable(at[k][c], 0, 1)

    # Each number from 1 to n^2 is written in exactly one square.
    for k in range(n_cells):
        solver.addConstraint([(1, at[k][c]) for c in range(n_cells)], True, 1, True, 1)

    # Each square holds exactly one number.
    for c in range(n_cells):
        solver.addConstraint([(1, at[k][c]) for k in range(n_cells)], True, 1, True, 1)

    # The grid shows in each square the number written there.
    for c in range(n_cells):
        i, j = divmod(c, n)
        solver.addConstraint([(k + 1, at[k][c]) for k in range(n_cells)] + [(-1, x[i][j])],
                             True, 0, True, 0)

    # If the number k + 1 is in square c, the number k + 2 is one allowed step from c.
    for k in range(n_cells - 1):
        for c in range(n_cells):
            solver.addConstraint([(1, at[k][c])] + [(-1, at[k + 1][d]) for d in reachable(c)],
                                 False, 0, True, 0)

    # If the number k + 2 is in square c, the number k + 1 is one allowed step from c.
    for k in range(n_cells - 1):
        for c in range(n_cells):
            solver.addConstraint([(1, at[k + 1][c])] + [(-1, at[k][d]) for d in reachable(c)],
                                 False, 0, True, 0)

    return solver, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
