"""
Model for calvin_puzzle problem.

Fill an n×n grid with numbers 1 to n² following movement rules:
- Type I (Horizontal/Vertical): next number placed exactly 3 squares away (2 square gap)
- Type II (Diagonal): next number placed exactly 2 squares away (1 square gap)
"""
from hermax.model import Model


def build(instance):
    n = instance["n"]
    m = Model()

    # Create n×n grid with values 1 to n²
    grid = m.int_matrix("grid", n, n, 1, n*n)

    # All values must be unique
    m &= grid.flatten().all_different()

    # For each value v from 1 to n²-1, ensure v+1 is placed at a valid neighbor
    for v in range(1, n*n):
        # Collect all valid positions for value v
        valid_moves = []

        # For each cell in the grid, if it contains v, v+1 must be at valid distance
        for i in range(n):
            for j in range(n):
                # If grid[i][j] = v, then v+1 must be at one of these positions:
                neighbors = []

                # Type I: Vertical moves (distance 3, i.e., 2 cells gap)
                if i + 3 < n:
                    neighbors.append((i+3, j))
                if i - 3 >= 0:
                    neighbors.append((i-3, j))

                # Type I: Horizontal moves (distance 3)
                if j + 3 < n:
                    neighbors.append((i, j+3))
                if j - 3 >= 0:
                    neighbors.append((i, j-3))

                # Type II: Diagonal moves (distance 2)
                if i + 2 < n and j + 2 < n:
                    neighbors.append((i+2, j+2))
                if i + 2 < n and j - 2 >= 0:
                    neighbors.append((i+2, j-2))
                if i - 2 >= 0 and j + 2 < n:
                    neighbors.append((i-2, j+2))
                if i - 2 >= 0 and j - 2 >= 0:
                    neighbors.append((i-2, j-2))

                # If grid[i][j] = v, then v+1 must be in one of the neighbor cells
                if neighbors:
                    neighbor_constraint = [grid[ni][nj] == v+1 for ni, nj in neighbors]
                    # At least one neighbor must contain v+1 when current cell contains v
                    m &= (grid[i][j] != v) | (sum(neighbor_constraint) >= 1)

    return m, {"x": grid}
