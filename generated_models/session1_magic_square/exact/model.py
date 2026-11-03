# session1_magic_square: an Exact (Python) model from DCP Rosetta.
# Download the `session1_magic_square.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_magic_square.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python session1_magic_square.py session1_magic_square.json

from exact import Exact


def create_model(instance):
    """Fill an n x n grid with the different whole numbers 1 to n^2 so that every
    row, every column and both diagonals add up to the same sum."""
    n = instance["n"]  # the side of the square: n rows and n columns
    # The sum every row, column and diagonal has to reach, n(n^2 + 1)/2
    magic_sum = n * (n * n + 1) // 2
    # The numbers the cells hold
    values = range(1, n * n + 1)

    solver = Exact()

    # square[i][j] is the number in row i, column j
    square = [[f"square_{i}_{j}" for j in range(n)] for i in range(n)]

    # Exact identifies its variables by name.
    # at[i][j][v] is 1 when cell (i, j) holds the number v, and 0 otherwise
    at = [[{} for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            solver.addVariable(square[i][j], 1, n * n)
            for v in values:
                at[i][j][v] = f"at_{i}_{j}_{v}"
                solver.addVariable(at[i][j][v], 0, 1)
            # Each cell holds exactly one number.
            solver.addConstraint([(1, at[i][j][v]) for v in values], True, 1, True, 1)
            # The number in the cell is the number v that its marks pick out.
            solver.addConstraint([(v, at[i][j][v]) for v in values] + [(-1, square[i][j])],
                                 True, 0, True, 0)

    # All numbers are different: each number sits in exactly one cell.
    for v in values:
        solver.addConstraint([(1, at[i][j][v]) for i in range(n) for j in range(n)], True, 1, True, 1)

    # Each row and each column adds up to the magic sum.
    for i in range(n):
        solver.addConstraint([(1, square[i][j]) for j in range(n)], True, magic_sum, True, magic_sum)
        solver.addConstraint([(1, square[j][i]) for j in range(n)], True, magic_sum, True, magic_sum)

    # Both diagonals add up to the magic sum.
    solver.addConstraint([(1, square[i][i]) for i in range(n)], True, magic_sum, True, magic_sum)
    solver.addConstraint([(1, square[i][n - 1 - i]) for i in range(n)], True, magic_sum, True, magic_sum)

    return solver, {"square": square}


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
