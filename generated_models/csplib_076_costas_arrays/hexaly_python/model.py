"""Costas array: a permutation of 1..n whose difference triangle has no repeated value in any row."""
import hexaly.optimizer as hx


def build(instance):
    n = instance["n"]  # number of marks, and side length of the n x n grid
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # perm[i] = 0-based row of the mark in column i; a list decision of size n holds each value at most once
    perm = model.list(n)
    # One mark per row and per column: the list must use all n values, so perm is a permutation of 0..n-1
    model.constraint(model.count(perm) == n)
    # costas[i] = X_{i+1}, the same permutation reported 1-based as the problem asks
    costas = [perm[i] + 1 for i in range(n)]

    # Each line of the difference triangle has no value twice:
    # line l (length n - l) holds the differences X_i - X_{i+l}, and these must be pairwise different
    # (posted as pairwise != constraints rather than as an all-different)
    for l in range(1, n):
        diffs = [costas[i] - costas[i + l] for i in range(n - l)]
        for a in range(len(diffs)):
            for b in range(a + 1, len(diffs)):
                model.constraint(diffs[a] != diffs[b])

    return optimizer, {"costas": costas}
