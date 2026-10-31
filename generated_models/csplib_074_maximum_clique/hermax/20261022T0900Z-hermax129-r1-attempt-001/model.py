from hermax.model import Model


def build(instance):
    n = instance["n"]
    adj = instance["adj"]

    m = Model()
    # c[i] is true when vertex i is in the clique.
    c = m.bool_vector("c", n)

    # A clique: every two distinct vertices in the subset are adjacent.
    # So two vertices with no edge between them cannot both be chosen.
    for i in range(n):
        for j in range(i + 1, n):
            if not adj[i][j]:
                m &= (~c[i]) | (~c[j])

    # Maximise the number of chosen vertices.
    # A soft clause on c[i] pays 1 when c[i] is false, so the total paid is the number left out.
    for i in range(n):
        m.obj[1] += c[i]

    return m, {"c": c}
