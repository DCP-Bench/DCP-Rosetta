from hermax.model import Model


def build(instance):
    n = instance["n"]

    m = Model()

    # Create n x n matrix with values 1 to n^2
    x = m.int_matrix("x", n, n, 1, n * n)

    # All elements must be distinct
    m &= x.flatten().all_different()

    # Compute bounds for the sums
    # Minimum sum: 1 + 2 + ... + n = n(n+1)/2
    # Maximum sum: (n^2 - n + 1) + ... + n^2 = n(n^2 + n + 1) / 2
    min_sum = n * (n + 1) // 2
    max_sum = n * (n * n + n + 1) // 2

    # Create an IntVector to hold the sums
    # We have n rows + n cols + 2 diagonals = 2n + 2 sums
    num_sums = 2 * n + 2
    sum_vars = m.int_vector("sums", num_sums, min_sum, max_sum)

    idx = 0

    # Row sums
    for i in range(n):
        row_terms = [x[i, j] for j in range(n)]
        m &= (sum_vars[idx] == sum(row_terms))
        idx += 1

    # Column sums
    for j in range(n):
        col_terms = [x[i, j] for i in range(n)]
        m &= (sum_vars[idx] == sum(col_terms))
        idx += 1

    # Main diagonal sum (top-left to bottom-right)
    diag_terms = [x[i, i] for i in range(n)]
    m &= (sum_vars[idx] == sum(diag_terms))
    idx += 1

    # Anti-diagonal sum (top-right to bottom-left)
    anti_diag_terms = [x[i, n - 1 - i] for i in range(n)]
    m &= (sum_vars[idx] == sum(anti_diag_terms))
    idx += 1

    # All sums must be different
    m &= sum_vars.all_different()

    return m, {"x": x}
