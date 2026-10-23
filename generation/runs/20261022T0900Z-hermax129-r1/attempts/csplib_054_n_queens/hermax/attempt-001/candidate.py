from hermax.model import Model


def build(instance):
    n = instance["n"]

    m = Model()
    queens = m.int_vector("queens", n, 1, n)

    # All queens in different columns
    m &= queens.all_different()

    # No two queens on the same diagonal
    for i in range(n):
        for j in range(i + 1, n):
            # queens[i] and queens[j] must not be on the same diagonal
            # They are on the same diagonal if |queens[i] - queens[j]| == |i - j|
            m &= (queens[i] - queens[j] != i - j)
            m &= (queens[i] - queens[j] != j - i)

    return m, {"queens": queens}
