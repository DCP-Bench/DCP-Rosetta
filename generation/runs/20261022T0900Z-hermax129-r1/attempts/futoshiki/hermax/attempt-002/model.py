"""Futoshiki - fill grid with numbers 1 to n satisfying row/column uniqueness and inequality constraints.

Grid must have each number 1 to n appearing once per row and once per column.
Inequality constraints between adjacent cells must be satisfied.
Indices in lt are 1-based.
"""

from hermax.model import Model


def build(instance):
    values = instance["values"]  # Pre-filled values
    lt = instance["lt"]  # Inequality constraints (1-indexed)

    n = len(values)  # Grid size

    m = Model()

    # Grid: grid[i][j] is a value from 1 to n
    grid = m.int_matrix("grid", n, n, 1, n)

    # Pre-filled constraints: if values[i][j] != 0, then grid[i][j] == values[i][j]
    for i in range(n):
        for j in range(n):
            if values[i][j] != 0:
                m &= (grid[i][j] == values[i][j])

    # Row uniqueness: each row has distinct values
    for i in range(n):
        m &= grid.row(i).all_different()

    # Column uniqueness: each column has distinct values
    for j in range(n):
        m &= grid.col(j).all_different()

    # Inequality constraints from lt (1-indexed)
    for constraint in lt:
        i1, j1, i2, j2 = constraint
        # Convert from 1-indexed to 0-indexed
        i1_0 = i1 - 1
        j1_0 = j1 - 1
        i2_0 = i2 - 1
        j2_0 = j2 - 1
        m &= (grid[i1_0][j1_0] < grid[i2_0][j2_0])

    outputs = {
        "grid": grid,
    }

    return m, outputs
