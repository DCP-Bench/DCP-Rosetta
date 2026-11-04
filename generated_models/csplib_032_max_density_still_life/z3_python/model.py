# csplib_032_max_density_still_life: a Z3 (Python) model from DCP Rosetta.
# Download the `csplib_032_max_density_still_life.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_032_max_density_still_life.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python csplib_032_max_density_still_life.py csplib_032_max_density_still_life.json

import z3


def create_model(instance):
    """On an n x m window of Conway's Game of Life, place as many live cells as possible so that
    the pattern does not change from one generation to the next. The board is infinite; cells
    outside the window are dead."""
    n = instance["n"]  # the number of rows of the window
    m = instance["m"]  # the number of columns of the window

    # grid[i][j] is true when the cell in row i, column j of the window is alive
    grid = [[z3.Bool(f"grid_{i}_{j}") for j in range(m)] for i in range(n)]

    # The number of live cells among the given cells.
    def live_count(cells):
        return z3.Sum([z3.If(cell, 1, 0) for cell in cells])

    # the stability rules of the window
    solver = z3.Optimize()

    # Stability inside the window: a live cell has 2 or 3 live neighbours and survives. A dead
    # cell does not have exactly 3 live neighbours, so it is not born.
    for i in range(n):
        for j in range(m):
            # the live cells among the neighbours of cell (i, j) inside the window
            live_neighbours = live_count([grid[a][b]
                                          for a in range(max(0, i - 1), min(n, i + 2))
                                          for b in range(max(0, j - 1), min(m, j + 2))
                                          if (a, b) != (i, j)])
            solver.add(z3.Implies(grid[i][j], z3.And(live_neighbours >= 2, live_neighbours <= 3)))
            solver.add(z3.Implies(z3.Not(grid[i][j]), live_neighbours != 3))

    # A dead cell just outside the window must not be born either, so it must not have exactly 3
    # live neighbours. The cell above or below column j sees the edge row in columns j - 1 to j + 1,
    # and the cell left or right of row i sees the edge column in rows i - 1 to i + 1.
    for j in range(m):
        solver.add(live_count([grid[0][a] for a in range(max(0, j - 1), min(m, j + 2))]) != 3)
        solver.add(live_count([grid[n - 1][a] for a in range(max(0, j - 1), min(m, j + 2))]) != 3)
    for i in range(n):
        solver.add(live_count([grid[a][0] for a in range(max(0, i - 1), min(n, i + 2))]) != 3)
        solver.add(live_count([grid[a][m - 1] for a in range(max(0, i - 1), min(n, i + 2))]) != 3)

    # Maximise the number of live cells in the window.
    solver.maximize(live_count([grid[i][j] for i in range(n) for j in range(m)]))

    return solver, {"grid": grid}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
