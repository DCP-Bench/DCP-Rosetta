"""Calvin Puzzle - fill an n×n grid with numbers 1 to n² following movement rules.

Movement Type I (vertical/horizontal): next number exactly 3 squares away (2-square gap).
Movement Type II (diagonal): next number exactly 2 squares away (1-square gap).
"""

from hermax.model import Model


def build(instance):
    n = instance["n"]
    grid_size = n * n

    m = Model()

    # Grid: x[i][j] is the number placed at position (i, j)
    x = m.int_matrix("x", n, n, 1, grid_size)

    # All values 1 to n² must be placed exactly once
    x_flat = x.flatten()
    m &= x_flat.all_different()

    # For each number k from 1 to n²-1, the number k+1 must be:
    # - Type I: exactly 3 squares away horizontally or vertically (positions where |dx|+|dy|=3 and (dx=0 or dy=0))
    # - Type II: exactly 2 squares away diagonally (positions where |dx|+|dy|=2 and dx≠0 and dy≠0)

    # Create position variables for each number
    pos_row = m.int_vector("pos_row", grid_size + 1, 0, n - 1)
    pos_col = m.int_vector("pos_col", grid_size + 1, 0, n - 1)

    # Constraint: pos_row[k] and pos_col[k] is the position of number k
    for i in range(n):
        for j in range(n):
            for k in range(1, grid_size + 1):
                m &= ((x[i][j] == k) | ((pos_row[k] != i) | (pos_col[k] != j)))

    # Actually, let me use a different approach: for each cell, if it contains k, then the cell containing k+1 must satisfy the movement constraint
    for i in range(n):
        for j in range(n):
            for k in range(1, grid_size):
                # If x[i][j] == k, then x[next_i][next_j] == k+1
                # and (next_i, next_j) must satisfy the movement constraint

                # Type I: horizontal or vertical, exactly 3 squares away
                # (next_i, next_j) is at (i±3, j) or (i, j±3)

                # Type II: diagonal, exactly 2 squares away
                # (next_i, next_j) is at (i±2, j±2)

                # Valid next positions for number k+1 when k is at (i, j)
                valid_positions = []

                # Type I: horizontal/vertical
                for di, dj in [(3, 0), (-3, 0), (0, 3), (0, -3)]:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < n and 0 <= nj < n:
                        valid_positions.append((ni, nj))

                # Type II: diagonal
                for di, dj in [(2, 2), (2, -2), (-2, 2), (-2, -2)]:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < n and 0 <= nj < n:
                        valid_positions.append((ni, nj))

                if valid_positions:
                    # If x[i][j] == k, then x[next_i][next_j] == k+1 for one of the valid positions
                    constraint = sum(x[ni][nj] == k + 1 for ni, nj in valid_positions)
                    # If x[i][j] == k, then at least one valid next position has k+1
                    m &= ((x[i][j] != k) | (constraint >= 1))

    outputs = {
        "x": x,
    }

    return m, outputs
