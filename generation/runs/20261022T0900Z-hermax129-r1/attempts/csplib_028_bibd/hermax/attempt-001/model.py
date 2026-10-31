from hermax.model import Model


def build(instance):
    # Balanced Incomplete Block Design (BIBD):
    # v objects into b blocks where:
    # - Each block has exactly k objects
    # - Each object appears in exactly r blocks
    # - Any two distinct objects appear together in exactly l blocks

    v = instance["v"]  # Number of objects (rows)
    b = instance["b"]  # Number of blocks (columns)
    r = instance["r"]  # Objects per block (wait, actually each object appears in r blocks)
    k = instance["k"]  # Each block has k objects
    l = instance["l"]  # Any two objects appear together in l blocks

    m = Model()

    # Incidence matrix: matrix[i][j] = 1 iff object i is in block j
    matrix = m.bool_matrix("matrix", v, b)

    # Constraint 1: Each row sums to r (each object appears in r blocks)
    for i in range(v):
        m &= sum(matrix.row(i)) == r

    # Constraint 2: Each column sums to k (each block has k objects)
    for j in range(b):
        m &= sum(matrix.col(j)) == k

    # Constraint 3: Scalar product of any two distinct rows is l
    # (any two objects appear together in l blocks)
    for i1 in range(v):
        for i2 in range(i1 + 1, v):
            # Count how many columns have 1 in both row i1 and i2
            # Create auxiliary variables for the AND operations
            and_vars = []
            for j in range(b):
                and_var = m.bool()
                # and_var is true iff matrix[i1][j] and matrix[i2][j] are both true
                # This means: and_var => (matrix[i1][j] & matrix[i2][j])
                #            (matrix[i1][j] & matrix[i2][j]) => and_var
                m &= (~and_var) | matrix[i1][j]
                m &= (~and_var) | matrix[i2][j]
                m &= (~matrix[i1][j]) | (~matrix[i2][j]) | and_var
                and_vars.append(and_var)
            inner_product = m.sum_var(and_vars)
            m &= (inner_product == l)

    return m, {"matrix": matrix}
