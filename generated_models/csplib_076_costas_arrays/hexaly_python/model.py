"""Costas array: a permutation of 1..n whose difference triangle has no repeated value in any row."""
import hexaly.optimizer as hx


def build(instance):
    n = instance["n"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # The marks form a permutation: a full list decision of 0..n-1, reported 1-based
    perm = model.list(n)
    model.constraint(model.count(perm) == n)
    costas = [perm[i] + 1 for i in range(n)]

    # Row l of the difference triangle holds X_i - X_{i+l}; its values are all different
    for l in range(1, n):
        diffs = [costas[i] - costas[i + l] for i in range(n - l)]
        for a in range(len(diffs)):
            for b in range(a + 1, len(diffs)):
                model.constraint(diffs[a] != diffs[b])

    return optimizer, {"costas": costas}
