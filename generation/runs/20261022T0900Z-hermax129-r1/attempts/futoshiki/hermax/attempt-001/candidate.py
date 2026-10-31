"""Futoshiki - fill grid with numbers 1 to n satisfying row/column uniqueness and inequality constraints.

Grid must have each number 1 to n appearing once per row and once per column.
Inequality constraints between adjacent cells must be satisfied.
"""

from hermax.model import Model


def build(instance):
    n = 5  # Standard futoshiki is 5x5
    values = instance["values"]  # Pre-filled values
    lt = instance["lt"]  # Inequality constraints (i1, j1, i2, j2) where grid[i1][j1] < grid[i2][j2]

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

    # Inequality constraints from lt
    for constraint in lt:
        i1, j1, i2, j2 = constraint
        m &= (grid[i1][j1] < grid[i2][j2])

    outputs = {
        "grid": grid,
    }

    return m, outputs
