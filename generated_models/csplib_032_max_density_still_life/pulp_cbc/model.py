# csplib_032_max_density_still_life: a PuLP (Python) model from DCP Rosetta.
# Download the `csplib_032_max_density_still_life.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_032_max_density_still_life.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python csplib_032_max_density_still_life.py csplib_032_max_density_still_life.json

import pulp


def create_model(instance):
    """Find the still life with the most live cells in an n x m active grid of Conway's Game of
    Life. A still life is a pattern that does not change from one generation to the next. Cells
    outside the active grid are dead."""
    n = instance["n"]  # rows of the active grid
    m = instance["m"]  # columns of the active grid

    problem = pulp.LpProblem("still_life", pulp.LpMaximize)

    # grid[i][j] is 1 when the cell in row i, column j is alive
    grid = [[pulp.LpVariable(f"grid_{i}_{j}", cat="Binary") for j in range(m)] for i in range(n)]

    for i in range(n):
        for j in range(m):
            # the cells of the active grid next to cell (i, j)
            around = [(i + di, j + dj)
                      for di in (-1, 0, 1) for dj in (-1, 0, 1)
                      if (di, dj) != (0, 0) and 0 <= i + di < n and 0 <= j + dj < m]
            live_neighbours = pulp.lpSum(grid[a][b] for a, b in around)
            # a cell has at most eight neighbours, which bounds the sums below
            most_neighbours = 8

            # A live cell has 2 or 3 live neighbours.
            problem += live_neighbours >= 2 * grid[i][j]
            problem += live_neighbours <= 3 + (most_neighbours - 3) * (1 - grid[i][j])

            # crowded[i][j] is 1 when the dead cell (i, j) has at least four live neighbours.
            crowded = pulp.LpVariable(f"crowded_{i}_{j}", cat="Binary")

            # A dead cell does not have exactly 3 live neighbours: it has at most 2, or at least 4.
            problem += live_neighbours <= 2 + (most_neighbours - 2) * (crowded + grid[i][j])
            problem += live_neighbours >= 4 * crowded - 4 * grid[i][j]

    # Dead cells just outside the active grid stay dead. The outside cell beside column j of the
    # top or bottom row touches the edge cells in columns j-1 to j+1, and at most two of them may
    # be alive. The same holds for the left and right columns.
    for j in range(m):
        for edge_row in (0, n - 1):
            edge = [grid[edge_row][jj] for jj in range(max(0, j - 1), min(m, j + 2))]
            problem += pulp.lpSum(edge) <= 2
    for i in range(n):
        for edge_col in (0, m - 1):
            edge = [grid[ii][edge_col] for ii in range(max(0, i - 1), min(n, i + 2))]
            problem += pulp.lpSum(edge) <= 2

    # Maximize the number of live cells.
    problem += pulp.lpSum(grid[i][j] for i in range(n) for j in range(m))

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
