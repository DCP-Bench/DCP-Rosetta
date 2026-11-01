from hermax.model import Model


def build(instance):
    n = instance["n"]
    cols = instance["m"]

    model = Model()
    grid = model.bool_matrix("grid", n, cols)

    # Neighbourhood of a cell: the eight surrounding positions (fixed geometry).
    offsets = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    for i in range(-1, n + 1):
        for j in range(-1, cols + 1):
            inside = 0 <= i < n and 0 <= j < cols
            # Only in-grid neighbours can be live; cells outside the grid are dead.
            lits = [grid[i + di][j + dj] for di, dj in offsets
                    if 0 <= i + di < n and 0 <= j + dj < cols]
            if len(lits) < 3:
                # Fewer than three possible live neighbours: exactly 3 is impossible.
                if not inside:
                    continue
            s = sum(lits)

            # A dead cell, including one just outside the grid, must not have exactly 3 live neighbours.
            if len(lits) >= 3:
                three = model.bool()
                model &= (s == 3).iff(three)
                if inside:
                    model &= (~three | grid[i][j])
                else:
                    model &= ~three

            if inside:
                # A live cell must have exactly 2 or 3 live neighbours.
                model &= (s >= 2).only_if(grid[i][j])
                model &= (s <= 3).only_if(grid[i][j])

    # Maximise the number of live cells in the active grid.
    for i in range(n):
        for j in range(cols):
            model.obj[1] += grid[i][j]

    return model, {"grid": grid}
