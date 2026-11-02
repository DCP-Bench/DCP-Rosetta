# heterosquare: an Exact (Python) model from DCP Rosetta.
# Download the `heterosquare.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/heterosquare.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python heterosquare.py heterosquare.json

from exact import Exact


def create_model(instance):
    """A heterosquare of order n is an n by n square of distinct integers from 1 to n^2
    whose row, column and diagonal sums are all different."""
    n = instance["n"]  # the order of the square
    cells = n * n      # the number of cells, which is also the largest number in the square

    solver = Exact()

    # Exact identifies its variables by name.
    # x[i][j] is the number in row i, column j
    x = [[f"x_{i}_{j}" for j in range(n)] for i in range(n)]
    # holds[i][j][v - 1] is 1 when cell (i, j) holds the number v, and 0 when not
    holds = [[[f"cell_{i}_{j}_holds_{v}" for v in range(1, cells + 1)] for j in range(n)]
             for i in range(n)]
    for i in range(n):
        for j in range(n):
            solver.addVariable(x[i][j], 1, cells)
            for name in holds[i][j]:
                solver.addVariable(name, 0, 1)
            # Each cell holds exactly one number, and x[i][j] is that number.
            solver.addConstraint([(1, name) for name in holds[i][j]], True, 1, True, 1)
            solver.addConstraint([(v, holds[i][j][v - 1]) for v in range(1, cells + 1)] + [(-1, x[i][j])],
                                 True, 0, True, 0)
    # Each number from 1 to n^2 is in at most one cell, so every number is used once.
    for v in range(cells):
        solver.addConstraint([(1, holds[i][j][v]) for i in range(n) for j in range(n)], False, 0, True, 1)

    # The smallest and the largest possible sum of n distinct numbers from 1 to n^2.
    low = n * (n + 1) // 2
    high = n * cells - n * (n - 1) // 2

    # The cells of each row, each column, the diagonal and the anti-diagonal.
    lines = [[(1, x[i][j]) for j in range(n)] for i in range(n)]
    lines += [[(1, x[i][j]) for i in range(n)] for j in range(n)]
    lines.append([(1, x[i][i]) for i in range(n)])
    lines.append([(1, x[i][n - i - 1]) for i in range(n)])

    # sums[k] is the total of the cells in lines[k]: first the n rows, then the n columns,
    # then the diagonal and the anti-diagonal.
    sums = [f"line_sum_{k}" for k in range(len(lines))]
    for name, line in zip(sums, lines):
        solver.addVariable(name, low, high)
        solver.addConstraint(line + [(-1, name)], True, 0, True, 0)

    # spread is more than the difference between any two line sums.
    spread = high - low + 1
    # The line sums are all different. For each pair of line sums, sum_a_exceeds_b is 1 when
    # sum a is the larger one, and 0 when sum b is.
    for a in range(len(sums)):
        for b in range(a + 1, len(sums)):
            larger = f"sum_{a}_exceeds_{b}"
            solver.addVariable(larger, 0, 1)
            solver.addConstraint([(1, sums[a]), (-1, sums[b]), (-spread, larger)], True, 1 - spread)
            solver.addConstraint([(1, sums[b]), (-1, sums[a]), (spread, larger)], True, 1)

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
