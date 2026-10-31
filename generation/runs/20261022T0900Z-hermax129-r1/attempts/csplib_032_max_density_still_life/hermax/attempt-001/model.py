from hermax.model import Model


def build(instance):
    n = instance["n"]
    m = instance["m"]

    model = Model()

    # grid[i][j] = 1 if cell (i, j) is alive, 0 if dead
    grid = model.bool_matrix("grid", n, m)

    # Helper to count neighbors
    def count_neighbors(i, j, include_self=False):
        """Count live neighbors around cell (i, j)"""
        # Neighbors include cells outside the active grid (they are dead)
        # But we need to count if dead cells just outside would be considered
        count = 0
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                if di == 0 and dj == 0:
                    if include_self:
                        count += grid[i][j]
                    continue
                ni, nj = i + di, j + dj
                if 0 <= ni < n and 0 <= nj < m:
                    count += grid[ni][nj]
                # If neighbor is outside grid, it's assumed dead (contributes 0)
        return count

    # Still life constraints:
    # 1. A live cell must have exactly 2 or 3 live neighbors to remain alive
    # 2. A dead cell must not have exactly 3 live neighbors (otherwise it becomes alive)

    # For each cell in the active grid
    for i in range(n):
        for j in range(m):
            neighbors = count_neighbors(i, j, include_self=False)

            # If grid[i][j] is alive (1)
            # Then neighbors must be 2 or 3
            # model &= (grid[i][j] == 0) | (neighbors == 2) | (neighbors == 3)
            # This is: if alive, then 2 or 3 neighbors
            model &= (~grid[i][j]) | (neighbors == 2) | (neighbors == 3)

            # If grid[i][j] is dead (0)
            # Then neighbors must not be 3
            # model &= (grid[i][j] == 1) | (neighbors != 3)
            # This is: if dead, then not exactly 3 neighbors
            model &= grid[i][j] | (~(neighbors == 3))

    # Also check cells just outside the active grid
    # These are always dead, so they must not have exactly 3 live neighbors
    # Cells outside grid include: (-1, -1) to (-1, m), (n, -1) to (n, m), etc.

    # Check cells just outside the border
    # Top row (i = -1)
    for j in range(-1, m + 1):
        neighbors = 0
        for di in [0, 1]:
            for dj in [-1, 0, 1]:
                ni, nj = -1 + di, j + dj
                if ni == 0 and 0 <= nj < m:
                    neighbors += grid[ni][nj]
        # Dead cell must not have exactly 3 neighbors
        model &= (~(neighbors == 3))

    # Bottom row (i = n)
    for j in range(-1, m + 1):
        neighbors = 0
        for di in [-1, 0]:
            for dj in [-1, 0, 1]:
                ni, nj = n - 1 + di, j + dj
                if 0 <= ni < n and 0 <= nj < m:
                    neighbors += grid[ni][nj]
        model &= (~(neighbors == 3))

    # Left column (j = -1)
    for i in range(n):
        neighbors = 0
        for di in [-1, 0, 1]:
            for dj in [0, 1]:
                ni, nj = i + di, -1 + dj
                if 0 <= ni < n and 0 <= nj < m:
                    neighbors += grid[ni][nj]
        model &= (~(neighbors == 3))

    # Right column (j = m)
    for i in range(n):
        neighbors = 0
        for di in [-1, 0, 1]:
            for dj in [-1, 0]:
                ni, nj = i + di, m - 1 + dj
                if 0 <= ni < n and 0 <= nj < m:
                    neighbors += grid[ni][nj]
        model &= (~(neighbors == 3))

    # Objective: maximize the number of live cells
    for cell_count in range(n * m, -1, -1):
        total = sum(grid[i][j] for i in range(n) for j in range(m))
        model.obj[1] += (~(total >= cell_count))

    return model, {"grid": grid}
