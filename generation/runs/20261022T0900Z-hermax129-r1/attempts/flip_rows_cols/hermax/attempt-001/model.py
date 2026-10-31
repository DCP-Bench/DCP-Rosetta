from hermax.model import Model


def build(instance):
    matrix = instance["input_matrix"]
    n_rows = len(matrix)
    n_cols = len(matrix[0])

    m = Model()

    # Create boolean vectors for row and column signs
    # True means sign is 1, False means sign is -1
    row_flip = m.bool_vector("row_flip", n_rows)
    col_flip = m.bool_vector("col_flip", n_cols)

    # Convert to -1/1: 2*bool - 1
    row_signs = [2 * row_flip[i] - 1 for i in range(n_rows)]
    col_signs = [2 * col_flip[j] - 1 for j in range(n_cols)]

    # Row sum constraints: sum(matrix[i][j] * col_signs[j]) * row_signs[i] >= 0
    for i in range(n_rows):
        row_sum = sum(matrix[i][j] * col_signs[j] for j in range(n_cols))
        m &= (row_sum * row_signs[i] >= 0)

    # Column sum constraints: sum(matrix[i][j] * row_signs[i]) * col_signs[j] >= 0
    for j in range(n_cols):
        col_sum = sum(matrix[i][j] * row_signs[i] for i in range(n_rows))
        m &= (col_sum * col_signs[j] >= 0)

    # Objective: minimize overall sum
    # Overall sum = sum(matrix[i][j] * row_signs[i] * col_signs[j] for all i, j)
    # Pay when the value is positive (to minimize total)
    total_sum = sum(matrix[i][j] * row_signs[i] * col_signs[j]
                    for i in range(n_rows) for j in range(n_cols))
    m.obj[1] += total_sum

    # Output row_signs and col_signs as -1/1 values
    return m, {
        "row_signs": [row_signs[i] for i in range(n_rows)],
        "col_signs": [col_signs[j] for j in range(n_cols)]
    }
