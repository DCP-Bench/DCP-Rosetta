# csplib_032_max_density_still_life: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `csplib_032_max_density_still_life.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_032_max_density_still_life.html
# Then run it on the first instance (after `pip install ortools`):
#   python csplib_032_max_density_still_life.py csplib_032_max_density_still_life.json

from ortools.sat.python import cp_model


def create_model(instance):
    """In an n x m window of Conway's Game of Life, place as many live cells as possible so that
    the pattern does not change from one generation to the next. The board is infinite; cells
    outside the window are dead."""
    n = instance["n"]  # the number of rows of the window
    m = instance["m"]  # the number of columns of the window

    model = cp_model.CpModel()

    # grid[i][j] is true when the cell in row i, column j of the window is alive
    grid = [[model.new_bool_var(f"grid_{i}_{j}") for j in range(m)] for i in range(n)]

    def neighbours(i, j):
        """The cells of the window next to cell (i, j)."""
        return [
            grid[a][b]
            for a in range(max(0, i - 1), min(n, i + 2))
            for b in range(max(0, j - 1), min(m, j + 2))
            if (a, b) != (i, j)
        ]

    # Stability inside the window: a live cell has 2 or 3 live neighbours and survives,
    # a dead cell does not have exactly 3 live neighbours and is not born.
    for i in range(n):
        for j in range(m):
            # the number of live neighbours of cell (i, j)
            n_live_neighbours = sum(neighbours(i, j))
            model.add(n_live_neighbours >= 2).only_enforce_if(grid[i][j])
            model.add(n_live_neighbours <= 3).only_enforce_if(grid[i][j])
            model.add(n_live_neighbours != 3).only_enforce_if(~grid[i][j])

    # Cells just outside the window are not born: along each edge, no 3 neighbouring
    # cells of the window are all alive.
    for j in range(m):
        model.add(sum(grid[0][a] for a in range(max(0, j - 1), min(m, j + 2))) != 3)
        model.add(sum(grid[n - 1][a] for a in range(max(0, j - 1), min(m, j + 2))) != 3)
    for i in range(n):
        model.add(sum(grid[a][0] for a in range(max(0, i - 1), min(n, i + 2))) != 3)
        model.add(sum(grid[a][m - 1] for a in range(max(0, i - 1), min(n, i + 2))) != 3)

    # Maximize the number of live cells in the window.
    model.maximize(sum(grid[i][j] for i in range(n) for j in range(m)))

    return model, {"grid": grid}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
