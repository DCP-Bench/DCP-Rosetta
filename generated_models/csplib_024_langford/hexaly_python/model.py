"""Langford: arrange two copies of 1..k so that the two copies of d have exactly d numbers between them."""
import hexaly.optimizer as hx


def build(instance):
    k = instance["k"]  # k = the numbers 1..k each appear twice, so the sequence has 2k entries
    length = 2 * k
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # first[d - 1] = position (0-based) of the first d in the sequence.
    # Upper bound (derived): the second d sits d + 1 positions later and must still fit,
    # so the first d starts no later than position 2k - d - 2.
    first = [model.int(0, length - d - 2) for d in range(1, k + 1)]
    # second[d - 1] = position of the second d: exactly d numbers lie between the two d's
    second = [first[d - 1] + d + 1 for d in range(1, k + 1)]

    # The two copies of every number occupy different positions: the 2k positions are all different,
    # so every position of the sequence holds exactly one number
    positions = first + second
    for a in range(length):
        for b in range(a + 1, length):
            model.constraint(positions[a] != positions[b])

    # sol[t] = the number at position t of the sequence (the d whose first or second copy is at t)
    sol = [model.sum(d * ((first[d - 1] == t) + (second[d - 1] == t)) for d in range(1, k + 1))
           for t in range(length)]
    return optimizer, {"sol": sol}
