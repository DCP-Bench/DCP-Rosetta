from hermax.model import Model


def build(instance):
    # Quasigroup existence problem: find an m x m Latin square satisfying QG3 property.
    # A Latin square is an m x m table where each row and column contains 0 to m-1 exactly once.
    # QG3 property: (a*b)*(b*a) = a for all a, b (where * is the multiplication defined by the table).

    m = instance["m"]

    quasigroup = Model()

    # The quasigroup table: entry [i][j] represents i * j
    table = quasigroup.int_matrix("table", m, m, 0, m - 1)

    # Latin square constraints: each row and column contains 0 to m-1 exactly once
    for i in range(m):
        quasigroup &= table.row(i).all_different()
        quasigroup &= table.col(i).all_different()

    # QG3 property: (a*b)*(b*a) = a for all a, b
    # table[a][b] represents a*b
    # table[b][a] represents b*a
    # table[table[a][b]][table[b][a]] should equal a

    for a in range(m):
        for b in range(m):
            ab = table.row(a)[b]        # a * b
            ba = table.row(b)[a]        # b * a
            # (a*b) * (b*a) = a
            # table[ab][ba] = a
            quasigroup &= (table.row(ab)[ba] == a)

    return quasigroup, {"quasigroup": table}
