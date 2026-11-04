# csplib_032_max_density_still_life: a CPMpy model from DCP Rosetta.
# Download the `csplib_032_max_density_still_life.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_032_max_density_still_life.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python csplib_032_max_density_still_life.py csplib_032_max_density_still_life.json

import cpmpy as cp


def create_model(instance):
    """In an n x m window of Conway's Game of Life, place as many live cells as possible so that
    the pattern does not change from one generation to the next. The board is infinite; cells
    outside the window are dead."""
    n = instance["n"]  # the number of rows of the window
    m = instance["m"]  # the number of columns of the window

    # grid[i, j] is true when the cell in row i, column j is alive
    grid = cp.boolvar(shape=(n, m), name="grid")

    model = cp.Model()

    # Stability of every cell in the window: a live cell has 2 or 3 live neighbours (so it
    # survives), a dead cell does not have exactly 3 (so no cell is born).
    for i in range(n):
        for j in range(m):
            neighbours = [grid[i + di, j + dj]
                          for di in (-1, 0, 1) for dj in (-1, 0, 1)
                          if (di, dj) != (0, 0) and 0 <= i + di < n and 0 <= j + dj < m]
            alive_neighbours = cp.sum(neighbours)
            model.add(grid[i, j].implies((alive_neighbours >= 2) & (alive_neighbours <= 3)))
            model.add((~grid[i, j]).implies(alive_neighbours != 3))

    # Stability outside the window: a dead cell just outside must not be born either, so it must
    # not have exactly 3 live neighbours. Above and below the window, the neighbours of the
    # outside cell next to column j are the window cells of the edge row in columns j-1 .. j+1.
    for j in range(m):
        cols = slice(max(0, j - 1), min(m, j + 2))
        model.add(cp.sum(grid[0, cols]) != 3)
        model.add(cp.sum(grid[n - 1, cols]) != 3)

    # Left and right of the window, likewise with the edge columns. (Outside cells diagonal to a
    # corner see at most one window cell, so they need no constraint.)
    for i in range(n):
        rows = slice(max(0, i - 1), min(n, i + 2))
        model.add(cp.sum(grid[rows, 0]) != 3)
        model.add(cp.sum(grid[rows, m - 1]) != 3)

    # Maximise the number of live cells in the window.
    model.maximize(cp.sum(grid))

    return model, {"grid": grid}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
