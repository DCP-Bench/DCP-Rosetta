# heterosquare: a PuLP (Python) model from DCP Rosetta.
# Download the `heterosquare.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/heterosquare.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python heterosquare.py heterosquare.json

import pulp


def create_model(instance):
    """A heterosquare of order n is an n by n square of distinct integers from 1 to n^2
    whose row, column and diagonal sums are all different."""
    n = instance["n"]  # the order of the square
    n_cells = n * n  # the square holds the numbers 1 to n_cells, each once

    problem = pulp.LpProblem("heterosquare", pulp.LpMinimize)

    # number_at[r][c][v] is 1 when the cell in row r, column c holds the number v + 1
    number_at = pulp.LpVariable.dicts(
        "number_at", (range(n), range(n), range(n_cells)), cat="Binary")
    # x[r][c] is the number in row r, column c
    x = [[pulp.LpVariable(f"x_{r}_{c}", 1, n_cells, cat="Integer") for c in range(n)]
         for r in range(n)]

    # Each cell holds exactly one number, and x[r][c] is that number.
    for r in range(n):
        for c in range(n):
            problem += pulp.lpSum(number_at[r][c][v] for v in range(n_cells)) == 1
            problem += x[r][c] == pulp.lpSum(
                (v + 1) * number_at[r][c][v] for v in range(n_cells))

    # Each number from 1 to n_cells is in exactly one cell.
    for v in range(n_cells):
        problem += pulp.lpSum(
            number_at[r][c][v] for r in range(n) for c in range(n)) == 1

    # The lines whose sums must differ, each as the list of its cells: the n rows, the
    # n columns, the main diagonal and the anti-diagonal.
    lines = [[(r, c) for c in range(n)] for r in range(n)]
    lines += [[(r, c) for r in range(n)] for c in range(n)]
    lines.append([(i, i) for i in range(n)])
    lines.append([(i, n - 1 - i) for i in range(n)])

    # A line has n different numbers in it, so its sum is at least 1 + ... + n and at
    # most the sum of the n largest numbers.
    low = n * (n + 1) // 2
    high = n * n_cells - n * (n - 1) // 2
    n_sums = high - low + 1

    # has_sum[k][s] is 1 when line k sums to low + s.
    has_sum = pulp.LpVariable.dicts(
        "has_sum", (range(len(lines)), range(n_sums)), cat="Binary")
    # Each line has exactly one sum, and that sum is the total of its cells.
    for k, line in enumerate(lines):
        problem += pulp.lpSum(has_sum[k][s] for s in range(n_sums)) == 1
        problem += pulp.lpSum(x[r][c] for r, c in line) == pulp.lpSum(
            (low + s) * has_sum[k][s] for s in range(n_sums))
    # Two lines never have the same sum.
    for s in range(n_sums):
        problem += pulp.lpSum(has_sum[k][s] for k in range(len(lines))) <= 1

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
