from hermax.model import Model


def build(instance):
    # Futoshiki: Latin square with inequality constraints
    values = instance["values"]
    lt = instance["lt"]  # Inequality constraints

    n = len(values)

    m = Model()

    # Grid: fill in values 1..n in each cell
    grid = m.int_matrix("grid", n, n, 1, n)

    # Each row contains 1..n exactly once
    for i in range(n):
        m &= grid.row(i).all_different()

    # Each column contains 1..n exactly once
    for j in range(n):
        m &= grid.col(j).all_different()

    # Clues: fix known values
    for i in range(n):
        for j in range(n):
            if values[i][j] != 0:
                m &= (grid[i][j] == values[i][j])

    # Inequality constraints
    # Format appears to be: [row, col, comparison_direction, neighbor_specification]
    # Let me interpret based on the data structure
    # lt has 4 elements per constraint; likely [row_1based, col_1based, row_2based, col_2based]
    # with implicit ordering (< if indices indicate left/top neighbor, > if right/bottom)

    for constraint in lt:
        r1, c1, r2, c2 = constraint
        # Convert to 0-based indexing
        row1, col1 = r1 - 1, c1 - 1
        row2, col2 = r2 - 1, c2 - 1

        # Determine relationship: typically grid[row1][col1] < grid[row2][col2]
        # if row2 == row1 and col2 > col1, then left < right
        # if row2 > row1 and col2 == col1, then top < bottom
        # Otherwise, infer from the numeric ordering
        if row1 == row2 and col2 == col1 + 1:
            # Horizontal: left < right
            m &= (grid[row1][col1] < grid[row2][col2])
        elif row2 == row1 + 1 and col1 == col2:
            # Vertical: top < bottom
            m &= (grid[row1][col1] < grid[row2][col2])
        elif row1 == row2 and col2 == col1 - 1:
            # Horizontal: left > right
            m &= (grid[row1][col1] > grid[row2][col2])
        elif row2 == row1 - 1 and col1 == col2:
            # Vertical: top > bottom
            m &= (grid[row1][col1] > grid[row2][col2])

    return m, {"grid": grid}
