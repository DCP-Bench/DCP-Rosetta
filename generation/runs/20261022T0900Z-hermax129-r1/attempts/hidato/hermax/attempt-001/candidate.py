"""Hidato - connect numbers in increasing order where consecutive numbers must touch."""

from hermax.model import Model


def build(instance):
    puzzle = instance["puzzle"]

    n = len(puzzle)
    m_size = len(puzzle[0])

    m = Model()

    # Grid: x[i][j] is a value from 1 to n*m_size
    grid = m.int_matrix("x", n, m_size, 1, n * m_size)

    # Pre-filled constraints
    for i in range(n):
        for j in range(m_size):
            if puzzle[i][j] != 0:
                m &= (grid[i][j] == puzzle[i][j])

    # All values 1 to n*m_size must appear exactly once (by all_different over flattened grid)
    grid_flat = grid.flatten()
    m &= grid_flat.all_different()

    # Consecutive numbers must be adjacent
    # For each number k from 1 to n*m_size-1, k and k+1 must be adjacent
    for k in range(1, n * m_size):
        # Find all adjacent pairs in the grid
        # For each cell (i,j) that contains k, there must be an adjacent cell containing k+1

        # Create constraints: for each cell, if it contains k, then one of its neighbors contains k+1
        for i in range(n):
            for j in range(m_size):
                # Adjacent cells (8 neighbors for interior cells)
                neighbors = []
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        if di == 0 and dj == 0:
                            continue
                        ni, nj = i + di, j + dj
                        if 0 <= ni < n and 0 <= nj < m_size:
                            neighbors.append((ni, nj))

                # If grid[i][j] == k, then at least one neighbor has k+1
                if neighbors:
                    neighbor_sum = sum(grid[ni][nj] == k + 1 for ni, nj in neighbors)
                    # Post constraint: if grid[i][j] == k, then neighbor_sum >= 1
                    m &= ((grid[i][j] != k) | (neighbor_sum >= 1))

    outputs = {
        "x": grid,
    }

    return m, outputs
