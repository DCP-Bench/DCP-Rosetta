from hermax.model import Model


def build(instance):
    # Quasigroup (Latin square) with QG3 property: (a*b)*(b*a) = a
    m = instance["m"]

    m_model = Model()

    # The quasigroup table: entry [i][j] represents i * j
    table = m_model.int_matrix("table", m, m, 0, m - 1)

    # Latin square constraints: each row and column contains 0 to m-1 exactly once
    for i in range(m):
        m_model &= table.row(i).all_different()
        m_model &= table.col(i).all_different()

    # QG3 property: (a*b)*(b*a) = a for all a, b
    # We need to express table[table[a][b]][table[b][a]] == a
    # Since we can't use dynamic indexing in hermax, we use implication:
    # For each possible value v1 of table[a][b] and v2 of table[b][a],
    # if those are the actual values, then table[v1][v2] must equal a.

    for a in range(m):
        for b in range(m):
            for v1 in range(m):
                for v2 in range(m):
                    # Implication: if table[a][b] == v1 and table[b][a] == v2,
                    # then table[v1][v2] == a
                    # Encoded as: (~(table[a][b] == v1) | ~(table[b][a] == v2) | (table[v1][v2] == a))
                    ab = table.row(a)[b]
                    ba = table.row(b)[a]
                    result = table.row(v1)[v2]
                    m_model &= ((ab != v1) | (ba != v2) | (result == a))

    return m_model, {"quasigroup": table}
