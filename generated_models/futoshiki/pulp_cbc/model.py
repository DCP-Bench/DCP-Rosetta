# futoshiki: a PuLP (Python) model from DCP Rosetta.
# Download the `futoshiki.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/futoshiki.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python futoshiki.py futoshiki.json

import pulp


def create_model(instance):
    """Futoshiki: fill an n by n grid with the numbers 1 to n so that every row and every
    column holds each number once. Some cells are given, and some pairs of neighbouring
    cells carry a sign saying which of the two holds the smaller number."""
    values = instance["values"]  # values[r][c] is the number given in row r, column c, or 0 for an empty cell
    lt = instance["lt"]  # lt[k] holds the cells (r1, c1) and (r2, c2) of the k-th sign, counted from 1: the number in (r1, c1) is smaller
    n_grid = len(values)  # the grid is n_grid cells on each side

    problem = pulp.LpProblem("futoshiki", pulp.LpMinimize)

    # put[r][c][v] is 1 when the cell in row r, column c holds the number v + 1, and 0 when not
    put = [[[pulp.LpVariable(f"put_{r}_{c}_{v}", cat="Binary") for v in range(n_grid)]
            for c in range(n_grid)] for r in range(n_grid)]

    # grid[r][c] is the number in the cell at row r, column c. A given cell is fixed to its given number.
    grid = []
    for r in range(n_grid):
        row = []
        for c in range(n_grid):
            given = values[r][c]
            low, high = (given, given) if given > 0 else (1, n_grid)
            row.append(pulp.LpVariable(f"grid_{r}_{c}", low, high, cat="Integer"))
        grid.append(row)

    # Each cell holds exactly one number, and grid reads that number.
    for r in range(n_grid):
        for c in range(n_grid):
            problem += pulp.lpSum(put[r][c]) == 1
            problem += grid[r][c] == pulp.lpSum((v + 1) * put[r][c][v] for v in range(n_grid))

    # Each row holds each number once.
    for r in range(n_grid):
        for v in range(n_grid):
            problem += pulp.lpSum(put[r][c][v] for c in range(n_grid)) == 1

    # Each column holds each number once.
    for c in range(n_grid):
        for v in range(n_grid):
            problem += pulp.lpSum(put[r][c][v] for r in range(n_grid)) == 1

    # Each sign holds. The numbers are whole, so the smaller cell holds at least one less than the larger.
    for r1, c1, r2, c2 in lt:
        problem += grid[r1 - 1][c1 - 1] + 1 <= grid[r2 - 1][c2 - 1]

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
