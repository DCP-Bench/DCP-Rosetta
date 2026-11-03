"""Langford: arrange two copies of 1..k so that the two copies of d have exactly d numbers between them."""
import hexaly.optimizer as hx


def build(instance):
    k = instance["k"]
    length = 2 * k
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # first[d - 1] is the position (0-based) of the first d; the second d is d + 1 positions later
    first = [model.int(0, length - d - 2) for d in range(1, k + 1)]
    second = [first[d - 1] + d + 1 for d in range(1, k + 1)]

    # The 2k positions are all different, so every position holds exactly one number
    positions = first + second
    for a in range(length):
        for b in range(a + 1, length):
            model.constraint(positions[a] != positions[b])

    # The number at each position of the sequence
    sol = [model.sum(d * ((first[d - 1] == t) + (second[d - 1] == t)) for d in range(1, k + 1))
           for t in range(length)]
    return optimizer, {"sol": sol}
