"""All-interval series: a permutation of 0..n-1 whose neighbouring intervals are a permutation of 1..n-1."""
import hexaly.optimizer as hx


def build(instance):
    n = instance["n"]  # number of pitch-classes (12 for the standard twelve), so the series has n notes
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # x[i] = pitch-class (0..n-1) at position i of the series; a list decision of size n holds each value at most once
    x = model.list(n)
    # Each pitch-class occurs exactly once: the list must use all n values, so x is a permutation of 0..n-1
    model.constraint(model.count(x) == n)

    # diffs[i] = interval in semitones between neighbouring notes i and i + 1; as the notes are distinct it lies in 1..n-1
    diffs = [model.abs(x[i + 1] - x[i]) for i in range(n - 1)]
    # The intervals cover the full set 1..n-1: the n - 1 intervals are all different, and with n - 1 values in 1..n-1
    # that makes them a permutation of 1..n-1
    model.constraint(model.count(model.distinct(model.array(diffs))) == n - 1)

    return optimizer, {"x": x, "diffs": diffs}
