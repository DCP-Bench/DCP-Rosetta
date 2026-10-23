from hermax.model import Model


def build(instance):
    # Extract instance data
    row_sums = instance["row_sums"]
    col_sums = instance["col_sums"]

    n_rows = len(row_sums)
    n_cols = len(col_sums)

    m = Model()

    # Create a 0/1 integer matrix
    matrix = m.int_matrix("matrix", n_rows, n_cols, 0, 1)

    # Constraints: each row sum matches the given row sum
    for i in range(n_rows):
        m &= (sum(matrix.row(i)) == row_sums[i])

    # Constraints: each column sum matches the given column sum
    for j in range(n_cols):
        m &= (sum(matrix.col(j)) == col_sums[j])

    return m, {"matrix": matrix}
