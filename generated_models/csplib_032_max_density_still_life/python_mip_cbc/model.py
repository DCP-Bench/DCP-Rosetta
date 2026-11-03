# csplib_032_max_density_still_life: a Python-MIP (Python) model from DCP Rosetta.
# Download the `csplib_032_max_density_still_life.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_032_max_density_still_life.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python csplib_032_max_density_still_life.py csplib_032_max_density_still_life.json

import mip


def create_model(instance):
    """In an n x m active grid of Conway's Game of Life, choose which cells are alive so that
    the pattern does not change from one generation to the next, with as many live cells as
    possible. Cells outside the grid are dead."""
    n_rows = instance["n"]  # the number of rows of the active grid
    n_cols = instance["m"]  # the number of columns of the active grid

    model = mip.Model(sense=mip.MAXIMIZE, solver_name="CBC")

    # grid[i][j] is 1 when the cell in row i, column j is alive, and 0 when it is dead
    grid = [[model.add_var(f"grid_{i}_{j}", var_type=mip.BINARY) for j in range(n_cols)]
            for i in range(n_rows)]

    def cell(i, j):
        # the alive variable of cell (i, j), or None when the cell lies outside the grid
        if 0 <= i < n_rows and 0 <= j < n_cols:
            return grid[i][j]
        return None

    def live_neighbours(i, j):
        # the alive variables of the neighbours of cell (i, j) that lie inside the grid
        terms = []
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                if di == 0 and dj == 0:
                    continue
                v = cell(i + di, j + dj)
                if v is not None:
                    terms.append(v)
        return terms

    # A live cell has 2 or 3 live neighbours, so it survives.
    # A dead cell is not limited by this rule.
    for i in range(n_rows):
        for j in range(n_cols):
            alive = grid[i][j]
            n_live = mip.xsum(live_neighbours(i, j))
            model.add_constr(n_live >= 2 * alive)
            model.add_constr(n_live <= 3 + 5 * (1 - alive))

    # A cell that is dead must not have exactly 3 live neighbours, or it would come alive.
    # This holds for the cells just outside the grid too.
    for i in range(-1, n_rows + 1):
        for j in range(-1, n_cols + 1):
            alive = cell(i, j)
            # 1 when the cell has 4 or more live neighbours, 0 when it has 2 or fewer
            crowded = model.add_var(f"crowded_{i + 1}_{j + 1}", var_type=mip.BINARY)
            n_live = mip.xsum(live_neighbours(i, j))
            if alive is None:
                model.add_constr(n_live <= 2 + 6 * crowded)
                model.add_constr(n_live >= 4 * crowded)
            else:
                model.add_constr(n_live <= 2 + 6 * crowded + 8 * alive)
                model.add_constr(n_live >= 4 * crowded - 4 * alive)

    # Maximise the number of live cells in the grid.
    model.objective = mip.xsum(grid[i][j] for i in range(n_rows) for j in range(n_cols))

    return model, {"grid": grid}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
