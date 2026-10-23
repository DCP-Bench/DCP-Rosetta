from hermax.model import Model


def build(instance):
    a = instance["input_matrix"]
    num_rows = len(a)
    num_cols = len(a[0])

    m = Model()
    # A sign is -1 or 1 (flip or keep). Outputs are these integers.
    row_sign = m.int_vector("row_sign", num_rows, -1, 1)
    col_sign = m.int_vector("col_sign", num_cols, -1, 1)
    for r in range(num_rows):
        m &= (row_sign[r] != 0)
    for c in range(num_cols):
        m &= (col_sign[c] != 0)

    # A cell is flipped exactly when its row and column signs differ:
    # flipped = (row is negative) xor (column is negative).
    flipped = [[m.bool() for _ in range(num_cols)] for _ in range(num_rows)]
    for r in range(num_rows):
        neg_row = (row_sign[r] == -1)
        for c in range(num_cols):
            x = flipped[r][c]
            neg_col = (col_sign[c] == -1)
            m &= (~x | neg_row | neg_col)
            m &= (~x | ~neg_row | ~neg_col)
            m &= (x | ~neg_row | neg_col)
            m &= (x | neg_row | ~neg_col)

    # The signed value of a cell is a when kept (~x) and -a when flipped (x).
    # Every row and every column must sum to a non-negative number.
    for r in range(num_rows):
        m &= (sum(a[r][c] * ~flipped[r][c] for c in range(num_cols))
              >= sum(a[r][c] * flipped[r][c] for c in range(num_cols)))
    for c in range(num_cols):
        m &= (sum(a[r][c] * ~flipped[r][c] for r in range(num_rows))
              >= sum(a[r][c] * flipped[r][c] for r in range(num_rows)))

    # Minimise the overall sum of the signed matrix.
    m.obj += (sum(a[r][c] * ~flipped[r][c] for r in range(num_rows) for c in range(num_cols))
              - sum(a[r][c] * flipped[r][c] for r in range(num_rows) for c in range(num_cols)))

    return m, {"row_signs": row_sign, "col_signs": col_sign}
