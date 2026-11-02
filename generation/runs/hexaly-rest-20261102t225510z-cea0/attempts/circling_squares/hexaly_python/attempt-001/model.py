"""Circling the squares: ten different numbers (of at most two figures) in a circle, each adjacent pair having the
same sum of squares as the diametrically opposite pair, with A = 16, B = 2, F = 8 and G = 14 given."""
import hexaly.optimizer as hx

NAMES = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "K"]  # round the circle
GIVEN = {"A": 16, "B": 2, "F": 8, "G": 14}


def build(instance):
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # Each square holds a whole number of at most two figures
    x = [model.int(1, 99) for _ in NAMES]
    for i, name in enumerate(NAMES):
        if name in GIVEN:
            model.constraint(x[i] == GIVEN[name])

    # The numbers are all different
    for a in range(10):
        for b in range(a + 1, 10):
            model.constraint(x[a] != x[b])
    # Two adjoining squares have the same sum of squares as the two diametrically opposite to them
    for i in range(10):
        j, k, l = (i + 1) % 10, (i + 5) % 10, (i + 6) % 10
        model.constraint(x[i] * x[i] + x[j] * x[j] == x[k] * x[k] + x[l] * x[l])

    return optimizer, dict(zip(NAMES, x))
