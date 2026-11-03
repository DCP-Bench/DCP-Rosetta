# csplib_032_max_density_still_life: a hermax (Python) model from DCP Rosetta.
# Download the `csplib_032_max_density_still_life.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_032_max_density_still_life.html
# Then run it on the first instance (after `pip install hermax`):
#   python csplib_032_max_density_still_life.py csplib_032_max_density_still_life.json

from hermax.model import Model


def create_model(instance):
    """Maximum density still life (CSPLib 032): choose which cells of an n x m active grid
    are alive so that the pattern is a still life of Conway's Game of Life, and the number
    of live cells is as large as possible. Cells outside the grid are dead, but they still
    take part: a dead cell, inside or outside the grid, must not have exactly 3 live
    neighbours, or it would come alive."""
    rows = instance["n"]   # n: number of rows of the active grid
    cols = instance["m"]   # m: number of columns of the active grid

    m = Model()

    # grid[i][j] is true when cell (i, j) of the active grid is alive
    grid = m.bool_matrix("grid", rows, cols)

    def in_grid(i, j):
        return 0 <= i < rows and 0 <= j < cols

    # Every cell of the active grid, and the ring of dead cells around it, is checked.
    for i in range(-1, rows + 1):
        for j in range(-1, cols + 1):
            inside = in_grid(i, j)
            # live neighbours of (i, j); only the cells of the active grid can be alive
            around = [grid[i + di][j + dj]
                      for di in (-1, 0, 1) for dj in (-1, 0, 1)
                      if (di, dj) != (0, 0) and in_grid(i + di, j + dj)]
            if not inside and len(around) < 3:
                # outside the grid with fewer than 3 possible neighbours: never exactly 3
                continue

            # neighbours[i][j]: how many of the cell's neighbours are alive
            neighbours = m.int(f"neighbours_{i + 1}_{j + 1}", 0, len(around))
            m &= (neighbours == sum(around))

            if inside:
                alive = grid[i][j]
                # A live cell needs 2 or 3 live neighbours to stay alive.
                m &= (neighbours >= 2) | ~alive
                m &= (neighbours <= 3) | ~alive
                # A dead cell must not have exactly 3 live neighbours, or it is born.
                m &= (neighbours != 3) | alive
            else:
                # A dead cell outside the grid must not have exactly 3 live neighbours.
                m &= (neighbours != 3)

    # Maximise the number of live cells: minimise the negated count.
    m.obj += -sum(grid[i][j] for i in range(rows) for j in range(cols))

    return m, {"grid": grid}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
