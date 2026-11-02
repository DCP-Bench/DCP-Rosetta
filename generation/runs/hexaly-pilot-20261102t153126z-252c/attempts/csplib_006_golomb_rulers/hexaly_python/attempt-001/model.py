"""Golomb ruler: size marks 0 = a_1 < ... < a_m whose pairwise differences are all distinct, of minimum length a_m."""
import hexaly.optimizer as hx


def build(instance):
    m = instance["size"]
    # A ruler with marks 0, 1, 3, 7, ..., 2^(m-1) - 1 is always Golomb, which bounds the optimum
    horizon = 2 ** (m - 1) - 1 if m > 1 else 0
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    marks = [model.int(0, horizon) for _ in range(m)]

    # The first mark is at 0 and the marks strictly increase
    model.constraint(marks[0] == 0)
    for i in range(m - 1):
        model.constraint(marks[i] < marks[i + 1])
    # All pairwise differences are distinct
    diffs = [marks[j] - marks[i] for i in range(m) for j in range(i + 1, m)]
    for a in range(len(diffs)):
        for c in range(a + 1, len(diffs)):
            model.constraint(diffs[a] != diffs[c])

    # Minimise the length of the ruler, its last mark
    length = marks[-1]
    model.minimize(length)
    return optimizer, {"marks": marks, "length": length}
