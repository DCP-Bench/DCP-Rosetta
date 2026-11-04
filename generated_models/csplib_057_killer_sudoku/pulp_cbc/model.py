# csplib_057_killer_sudoku: a PuLP (Python) model from DCP Rosetta.
# Download the `csplib_057_killer_sudoku.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_057_killer_sudoku.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python csplib_057_killer_sudoku.py csplib_057_killer_sudoku.json

import math

import pulp


def create_model(instance):
    """Fill an n x n grid with the numbers 1 to n so that every row, column and box
    holds each number once, and the numbers in each cage add up to the small number
    printed in its corner, with no number repeated inside a cage."""
    n = instance["n"]          # the side of the grid
    cages = instance["problem"]  # each cage: the sum in its corner, and its cells counted from 1
    box = math.isqrt(n)        # the side of a box (3 for the usual 9 x 9 grid)

    problem = pulp.LpProblem("killer_sudoku", pulp.LpMinimize)  # no objective: any filling that follows the rules will do

    # put[r][c][v] is 1 when the cell in row r, column c holds the number v + 1, and 0 when not
    put = pulp.LpVariable.dicts("put", (range(n), range(n), range(n)), cat="Binary")
    # x[r][c] is the number in the cell in row r, column c, from 1 to n
    x = [[pulp.LpVariable(f"x_{r}_{c}", 1, n, cat="Integer") for c in range(n)] for r in range(n)]

    # Each cell holds exactly one number, and x[r][c] is that number.
    for r in range(n):
        for c in range(n):
            problem += pulp.lpSum(put[r][c][v] for v in range(n)) == 1
            problem += x[r][c] == pulp.lpSum((v + 1) * put[r][c][v] for v in range(n))

    for v in range(n):
        # Each row holds the number v + 1 once.
        for r in range(n):
            problem += pulp.lpSum(put[r][c][v] for c in range(n)) == 1
        # Each column holds the number v + 1 once.
        for c in range(n):
            problem += pulp.lpSum(put[r][c][v] for r in range(n)) == 1
        # Each box holds the number v + 1 once.
        for top in range(0, n, box):
            for left in range(0, n, box):
                problem += pulp.lpSum(put[r][c][v]
                                      for r in range(top, top + box)
                                      for c in range(left, left + box)) == 1

    # Each cage adds up to its total, and no number appears twice inside it.
    for total, cells in cages:
        cells = [(r - 1, c - 1) for r, c in cells]
        problem += pulp.lpSum(x[r][c] for r, c in cells) == total
        for v in range(n):
            problem += pulp.lpSum(put[r][c][v] for r, c in cells) <= 1

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
