# csplib_054_n_queens: a PuLP (Python) model from DCP Rosetta.
# Download the `csplib_054_n_queens.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_054_n_queens.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python csplib_054_n_queens.py csplib_054_n_queens.json

import pulp


def create_model(instance):
    """Place n queens on an n x n chessboard so that no two queens are on the same
    row, column or diagonal."""
    n = instance["n"]  # the board size and the number of queens

    problem = pulp.LpProblem("n_queens", pulp.LpMinimize)  # no objective: any placement will do

    # on[r][c] is 1 when row r has a queen in column c + 1, and 0 when not
    on = [[pulp.LpVariable(f"on_{r}_{c}", cat="Binary") for c in range(n)]
          for r in range(n)]
    # queens[r] is the column, from 1 to n, of the queen in row r
    queens = [pulp.LpVariable(f"queens_{r}", 1, n, cat="Integer") for r in range(n)]

    # Each row has exactly one queen, and queens[r] is its column.
    for r in range(n):
        problem += pulp.lpSum(on[r]) == 1
        problem += queens[r] == pulp.lpSum((c + 1) * on[r][c] for c in range(n))

    # No two queens share a column.
    for c in range(n):
        problem += pulp.lpSum(on[r][c] for r in range(n)) <= 1

    # No two queens share a diagonal running down to the right, where the column minus the row is constant.
    for d in range(-(n - 1), n):
        problem += pulp.lpSum(on[r][r + d] for r in range(n) if 0 <= r + d < n) <= 1

    # No two queens share a diagonal running down to the left, where the column plus the row is constant.
    for s in range(2 * n - 1):
        problem += pulp.lpSum(on[r][s - r] for r in range(n) if 0 <= s - r < n) <= 1

    return problem, {"queens": queens}


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
