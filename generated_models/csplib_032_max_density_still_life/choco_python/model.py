# csplib_032_max_density_still_life: a Choco-solver (Python) model from DCP Rosetta.
# Download the `csplib_032_max_density_still_life.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_032_max_density_still_life.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python csplib_032_max_density_still_life.py csplib_032_max_density_still_life.json

from pychoco.model import Model


def window_cells(grid, top, left, height, width):
    """The cells of the height x width block whose top-left corner is at (top, left)."""
    return [grid[i][j] for i in range(top, top + height) for j in range(left, left + width)]


def create_model(instance):
    """In an n x m window of Conway's Game of Life, place as many live cells as possible so that
    the pattern does not change from one generation to the next. The board is infinite; cells
    outside the window are dead."""
    n_rows = instance["n"]     # the number of rows of the window
    n_columns = instance["m"]  # the number of columns of the window

    model = Model()

    # grid[i][j] is true when the cell in row i, column j is alive
    grid = [[model.boolvar(name=f"grid_{i}_{j}") for j in range(n_columns)] for i in range(n_rows)]

    # A dead cell with exactly 3 live neighbours would come alive, and a live cell survives only
    # with 2 or 3 live neighbours. Each allowed pair is (live neighbours, alive).
    allowed = [(k, 0) for k in range(9) if k != 3] + [(2, 1), (3, 1)]

    # Every cell in the window stays as it is: its live neighbours inside the window decide
    # whether it lives on.
    for i in range(n_rows):
        for j in range(n_columns):
            # the cells of the window next to cell (i, j)
            neighbours = [grid[i + di][j + dj]
                          for di in (-1, 0, 1) for dj in (-1, 0, 1)
                          if (di, dj) != (0, 0) and 0 <= i + di < n_rows and 0 <= j + dj < n_columns]
            n_live_neighbours = model.intvar(0, len(neighbours), name=f"live_neighbours_{i}_{j}")
            model.sum(neighbours, "=", n_live_neighbours).post()
            model.table([n_live_neighbours, grid[i][j]],
                        [pair for pair in allowed if pair[0] <= len(neighbours)]).post()

    # A dead cell just outside the window must not be born, so it must not see exactly 3 live
    # cells. Above and below the window it sees three consecutive cells of the edge row; beside
    # it, three consecutive cells of the edge column.
    for j in range(n_columns):
        columns = range(max(0, j - 1), min(n_columns, j + 2))
        model.sum([grid[0][c] for c in columns], "!=", 3).post()
        model.sum([grid[n_rows - 1][c] for c in columns], "!=", 3).post()
    for i in range(n_rows):
        rows = range(max(0, i - 1), min(n_rows, i + 2))
        model.sum([grid[r][0] for r in rows], "!=", 3).post()
        model.sum([grid[r][n_columns - 1] for r in rows], "!=", 3).post()

    # Limits on live cells in small blocks. They follow from the rules above; they are stated
    # here to narrow the search: a 3 x 3 block holds at most 6 live cells, a 2 x 3 or 3 x 2
    # block at most 4.
    caps = {(3, 3): 6, (2, 3): 4, (3, 2): 4}
    for (height, width), cap in caps.items():
        for top in range(n_rows - height + 1):
            for left in range(n_columns - width + 1):
                model.sum(window_cells(grid, top, left, height, width), "<=", cap).post()

    # the number of live cells in each block of up to 3 x 3 cells, within its limit
    block_counts = []
    for top in range(0, n_rows, 3):
        for left in range(0, n_columns, 3):
            height, width = min(3, n_rows - top), min(3, n_columns - left)
            block_count = model.intvar(0, caps.get((height, width), height * width),
                                       name=f"block_count_{top}_{left}")
            model.sum(window_cells(grid, top, left, height, width), "=", block_count).post()
            block_counts.append(block_count)

    # The number of live cells in the window, to be maximised.
    live = model.intvar(0, n_rows * n_columns, name="live")
    model.sum(block_counts, "=", live).post()

    return model, {"grid": grid}, {"objective": live, "maximize": True}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
