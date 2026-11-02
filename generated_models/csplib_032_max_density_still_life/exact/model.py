# csplib_032_max_density_still_life: an Exact (Python) model from DCP Rosetta.
# Download the `csplib_032_max_density_still_life.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_032_max_density_still_life.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python csplib_032_max_density_still_life.py csplib_032_max_density_still_life.json

from exact import Exact


def create_model(instance):
    """On an infinite board of Conway's Game of Life, place live cells in an n x m window so that
    the pattern does not change from one generation to the next, with as many live cells as
    possible. Cells outside the window are dead."""
    n = instance["n"]  # the number of rows of the window
    m = instance["m"]  # the number of columns of the window

    solver = Exact()

    # Exact identifies its variables by name.
    # grid[i][j] is 1 when the cell in row i, column j of the window is alive
    grid = [[f"grid_{i}_{j}" for j in range(m)] for i in range(n)]
    for i in range(n):
        for j in range(m):
            solver.addVariable(grid[i][j], 0, 1)

    def neighbours(i, j):
        """The window cells next to cell (i, j)."""
        return [grid[a][b]
                for a in range(max(0, i - 1), min(n, i + 2))
                for b in range(max(0, j - 1), min(m, j + 2))
                if (a, b) != (i, j)]

    # Each window cell is stable. A live cell has 2 or 3 live neighbours and survives.
    for i in range(n):
        for j in range(m):
            cell = grid[i][j]
            around = neighbours(i, j)
            count = [(1, name) for name in around]  # the live neighbours of cell (i, j)
            n_neighbours = len(around)
            solver.addConstraint(count + [(-2, cell)], True, 0)
            if n_neighbours > 3:
                solver.addConstraint(count + [(n_neighbours - 3, cell)], False, 0, True, n_neighbours)
            # A dead cell does not have exactly 3 live neighbours. side[i][j] is 0 when the live
            # neighbours number at most 2, and 1 when they number at least 4.
            if n_neighbours >= 3:
                side = f"side_{i}_{j}"
                solver.addVariable(side, 0, 1)
                solver.addConstraint(count + [(-1, cell), (-(n_neighbours - 2), side)], False, 0, True, 2)
                solver.addConstraint(count + [(-4, side), (2, cell)], True, 0)

    # Cells just outside the window are dead and must not be born. A cell beside the top or the
    # bottom row has three neighbours in that row, and at most 2 of them may be alive. The same
    # holds for a cell beside the left or the right column.
    for j in range(m):
        for row in (0, n - 1):
            window = [grid[row][jj] for jj in range(max(0, j - 1), min(m, j + 2))]
            if len(window) == 3:
                solver.addConstraint([(1, name) for name in window], False, 0, True, 2)
    for i in range(n):
        for col in (0, m - 1):
            window = [grid[ii][col] for ii in range(max(0, i - 1), min(n, i + 2))]
            if len(window) == 3:
                solver.addConstraint([(1, name) for name in window], False, 0, True, 2)

    # The number of live cells in the window, to be as large as possible.
    live_cells = [(1, grid[i][j]) for i in range(n) for j in range(m)]

    solver.setObjective(live_cells, minimize=False)

    return solver, {"grid": grid}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
