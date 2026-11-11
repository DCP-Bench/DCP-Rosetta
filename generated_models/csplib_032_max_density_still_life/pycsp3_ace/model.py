# csplib_032_max_density_still_life: a PyCSP3 model from DCP Rosetta.
# Download the `csplib_032_max_density_still_life.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_032_max_density_still_life.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python csplib_032_max_density_still_life.py csplib_032_max_density_still_life.json

from pycsp3 import *


def create_model(instance):
    """Find the most densely populated still life of Conway's Game of Life on an n x m active grid: a
    pattern of live and dead cells that does not change from one generation to the next, with as many
    live cells as possible. Cells outside the grid are dead. A live cell must have 2 or 3 live
    neighbours, and a dead cell, including a dead cell just outside the grid, must not have exactly 3."""
    n_rows = instance["n"]  # n, the number of rows of the active grid
    n_cols = instance["m"]  # m, the number of columns of the active grid
    max_neighbours = 8      # a cell has at most 8 neighbours

    # grid[i][j] is 1 when the cell in row i, column j of the active grid is alive
    grid = VarArray(size=[n_rows, n_cols], dom={0, 1})
    # neighbours[i][j] is the number of live neighbours of the cell in row i, column j
    neighbours = VarArray(size=[n_rows, n_cols], dom=range(max_neighbours + 1))

    # The (state, neighbour count) pairs that a grid cell may have: a live cell has 2 or 3 live neighbours,
    # a dead cell does not have exactly 3. Listing them as a table lets the solver prune on both at once.
    allowed = [(1, count) for count in (2, 3)] + [(0, count) for count in range(max_neighbours + 1) if count != 3]

    for i in range(n_rows):
        for j in range(n_cols):
            # The 3 x 3 block around the cell, clipped to the active grid, minus the cell itself, gives its neighbours.
            block = grid[max(i - 1, 0):min(i + 2, n_rows), max(j - 1, 0):min(j + 2, n_cols)]
            satisfy(
                neighbours[i][j] == Sum(block) - grid[i][j],
                Table(scope=[grid[i][j], neighbours[i][j]], supports=allowed),
            )

    # A dead cell just outside the active grid must not have exactly 3 live neighbours. Cells outside
    # the grid are dead, so the live cells of the 3 x 3 block around them are their neighbours.
    for i in range(-1, n_rows + 1):
        for j in range(-1, n_cols + 1):
            if not (0 <= i < n_rows and 0 <= j < n_cols):
                block = grid[max(i - 1, 0):min(i + 2, n_rows), max(j - 1, 0):min(j + 2, n_cols)]
                satisfy(Sum(block) != 3)

    # Not part of the problem statement, added to speed up the proof of optimality: a pattern and its reflections
    # or transpose have the same density, so only the lexicographically smallest (row by row) of them is kept.
    # Solutions symmetric to a kept one are therefore not reported, but an optimal pattern always remains.
    flat = [grid[i][j] for i in range(n_rows) for j in range(n_cols)]
    images = [
        [grid[i][n_cols - 1 - j] for i in range(n_rows) for j in range(n_cols)],  # left-right flip
        [grid[n_rows - 1 - i][j] for i in range(n_rows) for j in range(n_cols)],  # top-bottom flip
    ]
    if n_rows == n_cols:
        images.append([grid[j][i] for i in range(n_rows) for j in range(n_cols)])  # transpose
    satisfy(LexIncreasing([flat, image]) for image in images)

    # Maximise the number of live cells in the active grid.
    maximize(Sum(grid))

    return {"grid": grid}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is OPTIMUM:
        print("grid", "=")
        for row in outputs["grid"]:
            print(values(row))
    else:
        print("No solution:", status())
