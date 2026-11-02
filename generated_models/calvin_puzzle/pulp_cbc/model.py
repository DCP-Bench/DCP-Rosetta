# calvin_puzzle: a PuLP (Python) model from DCP Rosetta.
# Download the `calvin_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/calvin_puzzle.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python calvin_puzzle.py calvin_puzzle.json

import pulp


def create_model(instance):
    """Fill an n by n grid with the numbers 1 to n^2 in sequence. The next number goes either
    exactly three squares away horizontally or vertically, or exactly two squares away
    diagonally from the previous one."""
    n = instance["n"]  # the grid has n rows and n columns
    cells = [(i, j) for i in range(n) for j in range(n)]  # the squares, as (row, column)
    n_cells = n * n  # the number of squares, which is also the largest number written

    # Any grid that follows the rules is an answer, so the problem has no objective.
    problem = pulp.LpProblem("calvin_puzzle", pulp.LpMinimize)

    # x[i][j] is the number written in row i, column j
    x = [[pulp.LpVariable(f"x_{i}_{j}", 1, n_cells, cat="Integer") for j in range(n)]
         for i in range(n)]

    # The steps allowed from one square to the next: three squares along a row or column
    # (Movement Type I), or two squares along a diagonal (Movement Type II).
    steps = [(3, 0), (-3, 0), (0, 3), (0, -3), (2, 2), (2, -2), (-2, 2), (-2, -2)]

    # The squares one allowed step away from the square cell, staying on the grid.
    def reachable(cell):
        i, j = cell
        return [(i + a, j + b) for a, b in steps if 0 <= i + a < n and 0 <= j + b < n]

    # follow[c, d] is 1 when the number after the one in square c is written in square d.
    follow = {(c, d): pulp.LpVariable(f"follow_{c[0]}_{c[1]}_{d[0]}_{d[1]}", cat="Binary")
              for c in cells for d in reachable(c)}
    # next_moves[c] are the moves leaving square c, previous_moves[c] the moves entering it.
    next_moves = {c: [] for c in cells}
    previous_moves = {c: [] for c in cells}
    for (c, d), var in follow.items():
        next_moves[c].append(var)
        previous_moves[d].append(var)

    # Each square has at most one next number and at most one previous number.
    for c in cells:
        problem += pulp.lpSum(next_moves[c]) <= 1
        problem += pulp.lpSum(previous_moves[c]) <= 1

    # The n_cells numbers are joined by n_cells - 1 moves.
    problem += pulp.lpSum(follow.values()) == n_cells - 1

    # A move from square c to square d means the number in d is one more than the number in c.
    # n_cells is larger than any difference between two numbers, so the rule is off when the
    # move is not taken.
    for (c, d), var in follow.items():
        problem += x[d[0]][d[1]] - x[c[0]][c[1]] - 1 <= n_cells * (1 - var)
        problem += x[d[0]][d[1]] - x[c[0]][c[1]] - 1 >= -n_cells * (1 - var)

    # A square with no previous move holds 1. Numbers rise by one along every move, so no
    # moves can close a loop, and the moves form one path through all the squares.
    for c in cells:
        problem += x[c[0]][c[1]] <= 1 + (n_cells - 1) * pulp.lpSum(previous_moves[c])

    return problem, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
