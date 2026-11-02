# sudoku: a PuLP (Python) model from DCP Rosetta.
# Download the `sudoku.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/sudoku.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python sudoku.py sudoku.json

import math

import pulp


def create_model(instance):
    """Fill a 9 x 9 grid with the digits 1 to 9 so that every row, every column and every
    3 x 3 box holds each digit once, keeping the digits already given."""
    given = instance["input_grid"]  # given[r][c] is the digit in row r, column c, or 0 when the cell is empty
    n_digits = len(given)  # the digits 1 to n_digits, which is also the side of the grid
    box = math.isqrt(n_digits)  # the side of a box

    # No objective: any filling that fits the rules is an answer.
    problem = pulp.LpProblem("sudoku", pulp.LpMinimize)

    # put[r][c][d] is 1 when the cell in row r, column c holds digit d + 1.
    put = pulp.LpVariable.dicts("put", (range(n_digits), range(n_digits), range(n_digits)),
                                cat="Binary")

    # grid[r][c] is the digit in row r, column c. A given digit is the only value the cell can take.
    grid = [[pulp.LpVariable(f"grid_{r}_{c}", given[r][c] or 1, given[r][c] or n_digits,
                             cat="Integer")
             for c in range(n_digits)]
            for r in range(n_digits)]

    # Each cell holds exactly one digit, and grid[r][c] is that digit.
    for r in range(n_digits):
        for c in range(n_digits):
            problem += pulp.lpSum(put[r][c][d] for d in range(n_digits)) == 1
            problem += grid[r][c] == pulp.lpSum((d + 1) * put[r][c][d] for d in range(n_digits))

    # Each digit appears once in every row, every column and every box.
    for d in range(n_digits):
        # Each row holds digit d + 1 once.
        for r in range(n_digits):
            problem += pulp.lpSum(put[r][c][d] for c in range(n_digits)) == 1
        # Each column holds digit d + 1 once.
        for c in range(n_digits):
            problem += pulp.lpSum(put[r][c][d] for r in range(n_digits)) == 1
        # Each box holds digit d + 1 once.
        for top in range(0, n_digits, box):
            for left in range(0, n_digits, box):
                problem += pulp.lpSum(put[r][c][d]
                                      for r in range(top, top + box)
                                      for c in range(left, left + box)) == 1

    return problem, {"grid": grid}


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
