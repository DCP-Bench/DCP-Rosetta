# session1_magic_square: a PuLP (Python) model from DCP Rosetta.
# Download the `session1_magic_square.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_magic_square.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python session1_magic_square.py session1_magic_square.json

import pulp


def create_model(instance):
    """Fill an n x n grid with the numbers 1 to n^2 so that every row, column and
    diagonal adds up to the same sum."""
    n = instance["n"]  # the number of rows and columns of the square
    cells = n * n      # the number of cells, which is also the largest number used

    # The sum every row, column and diagonal must reach: the numbers 1 to n^2 add up
    # to n^2 * (n^2 + 1) / 2, shared equally among the n rows.
    magic_sum = n * (n ** 2 + 1) // 2

    problem = pulp.LpProblem("magic_square", pulp.LpMinimize)

    # put[r][c][v] is 1 when the cell in row r, column c holds the number v + 1, and 0 when not
    put = [[[pulp.LpVariable(f"put_{r}_{c}_{v}", cat="Binary") for v in range(cells)]
            for c in range(n)] for r in range(n)]

    # square[r][c] is the number in the cell in row r, column c
    square = [[pulp.LpVariable(f"square_{r}_{c}", 1, cells, cat="Integer") for c in range(n)]
              for r in range(n)]

    # Each cell holds exactly one number, and that number is the cell's value.
    for r in range(n):
        for c in range(n):
            problem += pulp.lpSum(put[r][c]) == 1
            problem += square[r][c] == pulp.lpSum((v + 1) * put[r][c][v] for v in range(cells))

    # Each number from 1 to n^2 is in exactly one cell, so all the numbers are different.
    for v in range(cells):
        problem += pulp.lpSum(put[r][c][v] for r in range(n) for c in range(n)) == 1

    # Every row and every column adds up to the magic sum.
    for r in range(n):
        problem += pulp.lpSum(square[r][c] for c in range(n)) == magic_sum
    for c in range(n):
        problem += pulp.lpSum(square[r][c] for r in range(n)) == magic_sum

    # Both diagonals add up to the magic sum.
    problem += pulp.lpSum(square[i][i] for i in range(n)) == magic_sum
    problem += pulp.lpSum(square[i][n - 1 - i] for i in range(n)) == magic_sum

    # No objective: any filling that meets the sums is an answer.
    return problem, {"square": square}


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
