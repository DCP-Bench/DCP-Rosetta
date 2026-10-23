from hermax.model import Model


def build(instance):
    # All-interval series of size n: x is a permutation of 0..n-1 and the absolute
    # differences between neighbours, diffs, form a permutation of 1..n-1.
    n = instance["n"]

    m = Model()

    # Pitch classes: a permutation of 0..n-1.
    x = m.int_vector("x", n, 0, n - 1)
    m &= x.all_different()

    # Interval vector: a permutation of 1..n-1.
    diffs = m.int_vector("diffs", n - 1, 1, n - 1)
    m &= diffs.all_different()

    # diffs[i] = |x[i+1] - x[i]|: the direction Boolean picks which of the two half-reified
    # equalities is enforced (x[i+1] is above x[i], or x[i] is above x[i+1]).
    for i in range(n - 1):
        up = m.bool()
        m &= (x[i + 1] == x[i] + diffs[i]).only_if(up)
        m &= (x[i] == x[i + 1] + diffs[i]).only_if(~up)

    return m, {"x": x, "diffs": diffs}
