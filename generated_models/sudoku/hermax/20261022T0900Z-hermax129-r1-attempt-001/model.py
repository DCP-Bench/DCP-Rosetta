"""Sudoku - fill 9x9 grid with digits 1-9 satisfying row, column, and 3x3 box constraints."""

from hermax.model import Model


def build(instance):
    input_grid = instance["input_grid"]

    n = 9
    box_size = 3

    m = Model()

    # Grid: grid[i][j] is a value from 1 to 9
    grid = m.int_matrix("grid", n, n, 1, n)

    # Pre-filled constraints
    for i in range(n):
        for j in range(n):
            if input_grid[i][j] != 0:
                m &= (grid[i][j] == input_grid[i][j])

    # Row uniqueness: each row has distinct values 1-9
    for i in range(n):
        m &= grid.row(i).all_different()

    # Column uniqueness: each column has distinct values 1-9
    for j in range(n):
        m &= grid.col(j).all_different()

    # 3x3 box uniqueness: each 3x3 box has distinct values 1-9
    for box_i in range(3):
        for box_j in range(3):
            box_vars = []
            for i in range(box_size):
                for j in range(box_size):
                    row = box_i * box_size + i
                    col = box_j * box_size + j
                    box_vars.append(grid[row][col])

            # Create a temporary vector for all_different constraint
            box_vector = m.int_vector(f"box_{box_i}_{box_j}", len(box_vars), 1, n)
            for idx, var in enumerate(box_vars):
                m &= (box_vector[idx] == var)
            m &= box_vector.all_different()

    outputs = {
        "grid": grid,
    }

    return m, outputs
